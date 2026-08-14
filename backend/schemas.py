import datetime
from pydantic import BaseModel, ConfigDict

class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    throws: list[int]
    game_id: int
    total_score: int
    date: datetime.datetime

class GameStoreRequest(BaseModel):
    throws: list[int]
    total_score: int

class GameListResponse(BaseModel):
    games: list[GameRead]