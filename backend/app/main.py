import logging
from contextlib import asynccontextmanager
from collections import defaultdict
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph.empower_graph import run_match_workflow
from app.schemas import MatchRequest, MatchResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory rate limiting (for production, use Redis or similar)
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds


def is_rate_limited(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    # Clean old requests outside the window
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if now - timestamp < RATE_LIMIT_WINDOW
    ]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return True

    # Add current request
    rate_limit_store[client_ip].append(now)
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("EmpowerHer API starting")
    yield
    logger.info("EmpowerHer API shutdown")


app = FastAPI(
    title="EmpowerHer API",
    description="AI-powered mentorship and job matching for women in tech and adjacent fields.",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "empowerher"}


@app.post("/api/match", response_model=MatchResponse)
def match(req: MatchRequest, request: Request):
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    logger.info(f"Received match request: {req.message[:100]}...")
    try:
        data = run_match_workflow(req.message)
        logger.info(f"Match completed successfully for: {req.message[:50]}...")
        return MatchResponse.model_validate(data)
    except Exception as e:
        logger.exception(f"Match workflow failed for: {req.message[:50]}...")
        raise HTTPException(status_code=500, detail=str(e)) from e
