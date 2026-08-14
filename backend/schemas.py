from pydantic import BaseModel, ConfigDict

class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    throws: list[int]
    game_id: int

class GameStoreRequest(BaseModel):
    throws: list[int]
    total: int

class GameListResponse(BaseModel):
    games: list[GameRead]