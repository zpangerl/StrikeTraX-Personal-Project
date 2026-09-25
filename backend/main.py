"""Handles verifying, packaging, sending, and receiving data to and from the database."""

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, settings
from models import Game
from schemas import GameListResponse, GameRead, GameStoreRequest
from scoring import calculate_score

app = FastAPI()

logger = logging.getLogger(__name__)

# Create limiter for rate limiting specific functions.
limiter = Limiter(key_func=get_remote_address)
# Attach rate limiter to app and add handler to turn exceeded limits into a 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Bring in environment variables to set up CORS, restrict methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"]
)

@app.get("/health")
def health_ping() -> bool:
    """Ping the database to wake a paused Azure SQL instance.

    Returns:
        True if the database responds successfully.

    Raises:
        HTTPException: 503 if the database is unreachable.
    """
    with Session(engine) as session:
        try:
            session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            # Database is most likely asleep, raise exception to signal retry.
            # 503 code to differentiate from generic 500 code.
            logger.exception("Health check failed, database unreachable")
            raise HTTPException(status_code=503, detail="Database unreachable")
        return True

@app.get("/games")
def retrieve_games(session_id: uuid.UUID) -> GameListResponse:
    """Retrieve the user's games from the database.

    Args:
        session_id: The user's session ID.

    Returns:
        A GameListResponse containing all games under the user's session ID.

    Raises:
        HTTPException: 503 if database operation fails.
    """
    with Session(engine) as session:
        try:
            raw_results = session.execute(
                select(Game).where(Game.session_id == session_id).order_by(Game.date.desc())
            ).scalars().all()
            converted = [GameRead.model_validate(item) for item in raw_results]

        except SQLAlchemyError:
            # Database error (most likely resuming database)
            # Database isn't on all the time, may have to wait a minute or two before trying again to let it resume.
            # 503 code to differentiate from generic 500 code.
            logger.exception("Failed to retrieve games from Database")
            raise HTTPException(status_code=503, detail="Failed to retrieve games, please try again")
    response = GameListResponse(games=converted)
    return response

@app.post("/games", status_code=201)
@limiter.limit("5/minute")
def store_game(request: Request, new_game: GameStoreRequest) -> bool:
    """Validate and save a completed game.

    Args:
        request: The request, used by the limiter.
        new_game: The new game to be saved in the database.

    Returns:
        True if adding game is successful. Game does not need to be returned.

    Raises:
        HTTPException: 422 if game is invalid or recalculated score doesn't match provided total,
        503 if database operation fails.
    """
    throws = new_game.throws
    total = new_game.total_score
    session_id = new_game.session_id
    # Recalculate the final score of the game. We never want to trust client data, always verify server-side.
    processed_game = calculate_score(throws)
    if (not processed_game["is_valid"] or processed_game["total"] != total):
        # If the game is invalid or the score doesn't match, reject the game outright.
        raise HTTPException(status_code=422, detail="Game is invalid!")
    # Store the game
    game_store = Game(total_score=total, throws=throws, session_id=session_id)
    with Session(engine) as session:
        try:
            session.add(game_store)
            session.commit()
        except SQLAlchemyError:
            # Database error (most likely resuming database)
            # Database isn't on all the time, may have to wait a minute or two before trying again to let it resume.
            # 503 code to differentiate from generic 500 code.
            logger.exception("Failed to add new game to Database")
            raise HTTPException(status_code=503, detail="Failed to add game to database, please try again")
    return True