import datetime
import uuid
from pydantic import BaseModel, ConfigDict

class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    throws: list[int]
    game_id: int
    total_score: int
    date: datetime.datetime
    session_id: uuid.UUID

class GameStoreRequest(BaseModel):
    throws: list[int]
    total_score: int
    session_id: uuid.UUID

class GameListResponse(BaseModel):
    games: list[GameRead]