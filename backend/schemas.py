"""Pydantic schemas for defining request and response bodies."""

import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class GameRead(BaseModel):
    """A saved game, as returned to the client."""
    # Required for handling objects without converting them to dictionaries.
    model_config = ConfigDict(from_attributes=True)
    throws: list[int]
    game_id: int
    total_score: int
    date: datetime.datetime
    # Use UUID for now, will be user ID after phase 4.
    session_id: uuid.UUID

class GameStoreRequest(BaseModel):
    """Request for sending games to database."""
    throws: list[int] = Field(max_length=21)
    total_score: int
    session_id: uuid.UUID

class GameListResponse(BaseModel):
    """Response with list of all of the user's games from database."""
    games: list[GameRead]