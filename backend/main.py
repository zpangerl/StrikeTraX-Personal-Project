import logging
from database import engine
from fastapi import FastAPI, HTTPException
from models import Game
from schemas import GameStoreRequest
from scoring import calculate_score
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.post("/games", status_code=201)
def store_game(new_game: GameStoreRequest):
    throws = new_game.throws
    total = new_game.total
    processed_game = calculate_score(throws)
    if (not processed_game["is_valid"] or processed_game["total"] != total):
        # return validation error
        raise HTTPException(status_code=422, detail="Game is invalid!")
    # store the game
    game_store = Game(total_score=total, throws=throws)
    with Session(engine) as session:
        try:
            session.add(game_store)
            session.commit()
        except SQLAlchemyError as e:
            logging.exception("Failed to add game to database")
            raise HTTPException(status_code=500, detail="Failed to add game to database, please try again")
    return True