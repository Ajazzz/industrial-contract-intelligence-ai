import os

from dotenv import load_dotenv


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

import hashlib

cohere_key = os.getenv("COHERE_API_KEY", "")
groq_key = os.getenv("GROQ_API_KEY", "")

print("=" * 60)
print("ENV PATH EXISTS:", os.path.exists(ENV_PATH))
print("COHERE EXISTS:", bool(cohere_key))
print("COHERE HASH:", hashlib.sha256(cohere_key.encode()).hexdigest()[:12] if cohere_key else "None")
print("GROQ EXISTS:", bool(groq_key))
print("=" * 60)

print("INDEX_NAME:", os.getenv("INDEX_NAME"))

# ─────────────────────────────────────────────
# FASTAPI INIT
# ─────────────────────────────────────────────
app = FastAPI(
    title="Industrial Contract Intelligence API",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
ALLOWED_ORIGINS = [

    # Local Development
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Production Frontend
    "https://industrial-contract-intelligence-ai.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
from backend.routes.query import router as query_router

app.include_router(
    query_router,
    prefix="/api"
)

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/health")
async def health_check():

    return {
        "status": "healthy"
    }