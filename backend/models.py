"""SQLAlchemy models for defining database tables."""

import datetime
import uuid

from sqlalchemy import JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Game(Base):
    """SQLAlchemy model for Game object, maps to game table in database."""
    __tablename__ = "game"
    game_id: Mapped[int] = mapped_column(primary_key=True)
    total_score: Mapped[int]
    # Needs to be JSON, not a fixed length list.
    throws: Mapped[list[int]] = mapped_column(JSON)
    # Create date at time of insertion into database.
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Use UUID for now, will be user ID in the future.
    # Will include a users table to cross-reference with in the future.
    session_id: Mapped[uuid.UUID] = mapped_column(index=True)