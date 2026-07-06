import os
import time
import uuid
import cohere

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from backend.services.document_classifier import (
    classify_document
)

from backend.services.hybrid_chunker import (
    hybrid_chunk_page
)

# ─────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_PATH = os.path.join(
    BASE_DIR,
    "..",
    ".env"
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

load_dotenv(ENV_PATH)

PINECONE_API_KEY = os.getenv(
    "PINECONE_API_KEY"
)

INDEX_NAME = os.getenv(
    "INDEX_NAME"
)

COHERE_API_KEY = os.getenv(
    "COHERE_API_KEY"
)

if not PINECONE_API_KEY:
    raise ValueError(
        "PINECONE_API_KEY missing"
    )

if not INDEX_NAME:
    raise ValueError(
        "INDEX_NAME missing"
    )

if not COHERE_API_KEY:
    raise ValueError(
        "COHERE_API_KEY missing"
    )

# ─────────────────────────────────────────────
# INIT CLIENTS
# ─────────────────────────────────────────────
co = cohere.Client(
    COHERE_API_KEY
)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

# ─────────────────────────────────────────────
# CREATE / CONNECT INDEX
# ─────────────────────────────────────────────
existing_indexes = [
    i.name for i in pc.list_indexes()
]

if INDEX_NAME not in existing_indexes:

    print(
        f"Creating index: {INDEX_NAME}"
    )

    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

else:

    print(
        f"Using existing index: {INDEX_NAME}"
    )

index = pc.Index(INDEX_NAME)

# ─────────────────────────────────────────────
# DOCUMENT METADATA
# ─────────────────────────────────────────────
def extract_document_metadata(
    filename
):

    lower_name = filename.lower()

    metadata = {

        "document_type":
            "industrial_contract",

        "industry":
            "steel",

        "service_type":
            "general",

        "source":
            filename,

        # NEW FIELDS
        "contract_id":
            "enviri_jsw_isa_v3",

        "language":
            "en"
    }

    # ─────────────────────────────────────────
    # LANGUAGE DETECTION
    # ─────────────────────────────────────────
    if "_fr_" in lower_name or "francais" in lower_name:

        metadata["language"] = "fr"

    elif "_es_" in lower_name or "espanol" in lower_name:

        metadata["language"] = "es"

    else:

        metadata["language"] = "en"

    # ─────────────────────────────────────────
    # SERVICE TYPE
    # ─────────────────────────────────────────
    if "slag" in lower_name:

        metadata["service_type"] = (
            "slag_handling"
        )

    elif "furnace" in lower_name:

        metadata["service_type"] = (
            "furnace_installation"
        )

    elif "oxygen" in lower_name:

        metadata["service_type"] = (
            "oxygen_prs"
        )

    elif "excavation" in lower_name:

        metadata["service_type"] = (
            "excavation"
        )

    return metadata

# ─────────────────────────────────────────────
# EMBEDDINGS
# ─────────────────────────────────────────────
def embed_batch(texts):

    retries = 5

    for attempt in range(retries):

        try:

            response = co.embed(
                texts=texts,
                model="embed-multilingual-v3.0",
                input_type="search_document",
                embedding_types=["float"]
            )

            return response.embeddings.float

        except Exception as e:

            print(
                f"Embedding error: {e}"
            )

            wait_time = (
                (attempt + 1) * 10
            )

            print(
                f"Retrying in "
                f"{wait_time} sec..."
            )

            time.sleep(wait_time)

    raise Exception(
        "Embedding failed after retries"
    )

# ─────────────────────────────────────────────
# INDEX SINGLE PDF
# ─────────────────────────────────────────────
def index_pdf(pdf_path):

    filename = os.path.basename(
        pdf_path
    )

    print(
        f"\n📄 Processing: "
        f"{filename}"
    )

    doc_metadata = (
        extract_document_metadata(
            filename
        )
    )

    print(
        f"Metadata: "
        f"{doc_metadata}"
    )

    # ─────────────────────────────────────────
    # PAGE CLASSIFICATION
    # ─────────────────────────────────────────
    print(
        "Classifying document pages..."
    )

    classified_pages = (
        classify_document(
            pdf_path
        )
    )

    print(
        f"Total classified pages: "
        f"{len(classified_pages)}"
    )

    # ─────────────────────────────────────────
    # HYBRID CHUNKING
    # ─────────────────────────────────────────
    print(
        "Creating hybrid enterprise chunks..."
    )

    chunks = []

    for page_data in classified_pages:

        page_chunks = (
            hybrid_chunk_page(
                page_data
            )
        )

        chunks.extend(page_chunks)

    print(
        f"Total hybrid chunks: "
        f"{len(chunks)}"
    )

    # ─────────────────────────────────────────
    # UPSERT
    # ─────────────────────────────────────────
    batch_size = 2

    for i in range(
        0,
        len(chunks),
        batch_size
    ):

        batch = chunks[
            i:i + batch_size
        ]

        texts = [
            b["text"]
            for b in batch
        ]

        embeddings = embed_batch(
            texts
        )

        vectors = []

        for j, embedding in enumerate(
            embeddings
        ):

            chunk_data = batch[j]

            vectors.append({

                "id":
                    str(uuid.uuid4()),

                "values":
                    embedding,

                "metadata": {

                    "text":
                        chunk_data["text"],
                
                    "source":
                        doc_metadata["source"],
                
                    "document_type":
                        doc_metadata[
                            "document_type"
                        ],
                
                    "industry":
                        doc_metadata[
                            "industry"
                        ],
                
                    "service_type":
                        doc_metadata[
                            "service_type"
                        ],
                
                    # NEW
                    "language":
                        doc_metadata[
                            "language"
                        ],
                
                    # NEW
                    "contract_id":
                        doc_metadata[
                            "contract_id"
                        ],
                
                    "page":
                        chunk_data["page"],
                
                    "page_type":
                        chunk_data[
                            "page_type"
                        ],
                
                    "chunk_type":
                        chunk_data[
                            "chunk_type"
                        ]
                }
            })

        index.upsert(
            vectors=vectors
        )

        print(
            f"Uploaded batch "
            f"{i // batch_size + 1}"
        )

        time.sleep(3)

    print(
        f"✅ Finished indexing: "
        f"{filename}"
    )

# ─────────────────────────────────────────────
# INDEX ALL PDFs
# ─────────────────────────────────────────────
def index_all_pdfs():

    if not os.path.exists(DATA_DIR):

        raise FileNotFoundError(
            f"Data folder missing: "
            f"{DATA_DIR}"
        )

    pdf_files = [

        f for f in os.listdir(
            DATA_DIR
        )

        if f.lower().endswith(
            ".pdf"
        )
    ]

    if not pdf_files:

        raise FileNotFoundError(
            "No PDF files found"
        )

    print(
        f"\nFound "
        f"{len(pdf_files)} PDFs"
    )

    for pdf_file in pdf_files:

        pdf_path = os.path.join(
            DATA_DIR,
            pdf_file
        )

        index_pdf(pdf_path)

    print(
        "\n🎉 ALL DOCUMENTS INDEXED"
    )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":

    index_all_pdfs()