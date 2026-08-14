from pydantic import BaseModel

class Game(BaseModel):
    throws: list[int]
    id: int

class GameStoreRequest(BaseModel):
    throws: list[int]
    total: int

class GameListResponse(BaseModel):
    games: list[Game]