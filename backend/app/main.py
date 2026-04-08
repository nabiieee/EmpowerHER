import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph.empower_graph import run_match_workflow
from app.schemas import MatchRequest, MatchResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
def match(req: MatchRequest):
    logger.info(f"Received match request: {req.message[:100]}...")
    try:
        data = run_match_workflow(req.message)
        logger.info(f"Match completed successfully for: {req.message[:50]}...")
        return MatchResponse.model_validate(data)
    except Exception as e:
        logger.exception(f"Match workflow failed for: {req.message[:50]}...")
        raise HTTPException(status_code=500, detail=str(e)) from e
