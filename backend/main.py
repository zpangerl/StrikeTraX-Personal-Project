import logging
from database import engine
from fastapi import FastAPI, HTTPException
from models import Game
from schemas import GameStoreRequest, GameListResponse, GameRead
from scoring import calculate_score
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/games")
def retrieve_games():
    with Session(engine) as session:
        try:
            raw_results = session.execute(select(Game)).scalars().all()
            converted = [GameRead.model_validate(item) for item in raw_results]

        except SQLAlchemyError as e:
            logging.exception("Failed to retrieve games from database")
            raise HTTPException(status_code=500, detail="Failed to retrieve games, please try again")
    response = GameListResponse(games=converted)
    return response

@app.post("/games", status_code=201)
def store_game(new_game: GameStoreRequest):
    throws = new_game.throws
    total = new_game.total_score
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