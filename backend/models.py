from sqlalchemy import JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime


class Base(DeclarativeBase):
    pass

class Game(Base):
    __tablename__ = "game"
    game_id: Mapped[int] = mapped_column(primary_key=True)
    total_score: Mapped[int]
    throws: Mapped[list[int]] = mapped_column(JSON)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())