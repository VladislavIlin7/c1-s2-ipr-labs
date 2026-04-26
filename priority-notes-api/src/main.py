import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.config import get_settings
from src.schemas import ErrorResponse, Note, NoteCategory, NoteCreate, Stats
from src.services.notes_service import NoteNotFoundError, NotesService
from src.storage.redis_client import create_redis_client, get_redis_client

settings = get_settings()
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await create_redis_client()
    try:
        await redis_client.ping()
        logger.info("Redis connection is ready")
    except RedisError:
        logger.exception("Redis connection check failed")
    finally:
        await redis_client.aclose()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)


def get_notes_service(redis_client: Annotated[Redis, Depends(get_redis_client)]) -> NotesService:
    return NotesService(redis_client)


@app.get("/health")
async def health(redis_client: Annotated[Redis, Depends(get_redis_client)]) -> dict[str, str]:
    try:
        await redis_client.ping()
    except RedisError as exc:
        logger.exception("Health check failed")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is unavailable") from exc
    return {"status": "ok"}


@app.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    service: Annotated[NotesService, Depends(get_notes_service)],
) -> Note:
    return await service.create_note(payload)


@app.get("/notes", response_model=list[Note])
async def list_notes(service: Annotated[NotesService, Depends(get_notes_service)]) -> list[Note]:
    return await service.list_notes()


@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str, service: Annotated[NotesService, Depends(get_notes_service)]) -> Note:
    try:
        return await service.get_note(note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, service: Annotated[NotesService, Depends(get_notes_service)]) -> Response:
    try:
        await service.delete_note(note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/notes/category/{category}", response_model=list[Note])
async def list_notes_by_category(
    category: NoteCategory,
    service: Annotated[NotesService, Depends(get_notes_service)],
) -> list[Note]:
    return await service.list_notes_by_category(category)


@app.get("/stats", response_model=Stats)
async def get_stats(service: Annotated[NotesService, Depends(get_notes_service)]) -> Stats:
    return await service.get_stats()

