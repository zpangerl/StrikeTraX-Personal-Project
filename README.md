# StrikeTraX

StrikeTraX is a bowling score tracking web application that allows for live throw-by-throw updates, saving/loading in progress games, and displaying completed game history.

Please note, because the Azure SQL Database is serverless, it pauses after some time (App Service pauses as well). The first request may take a minute or two while the app and database start up. While waiting, a load screen will be displayed.

![Home page](src/assets/HomePage.png)
![Scoring page](src/assets/LogGame.png)
![History page](src/assets/History.png)

## Features

* Full, live, ten-pin scoring, including all 10th frame special cases
* Reactive display of current game state, including strikes, spares, rolling total, and current frame/roll
* Save/load for incomplete game, validation and storage still done locally
* Game history with persistence, via the Azure SQL database
* Easy navigation through a nav bar and Vue Router
* Responsive, mobile-friendly layout

## Tech Stack

- [Vue 3](https://vuejs.org/) (Composition API)
- [Vite](https://vitejs.dev/)
- [Vue Router](https://router.vuejs.org/)
- [Bootstrap 5](https://getbootstrap.com/) via the [Bootswatch](https://bootswatch.com/) Darkly theme
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic.dev/)
- [Azure SQL](https://azure.microsoft.com/en-us/products/azure-sql/database)
- [SlowAPI](https://slowapi.readthedocs.io/en/latest/)

## Getting Started

You must have the following things installed before starting:

- Node 20.19.0+ (within the 20.x line), or 22.12.0+.
- Python 3.12
- uv
- ODBC Driver 18 for SQL Server
- An Azure SQL database, a free one is enough

Clone the repository and install dependencies:

```sh
git clone https://github.com/zpangerl/StrikeTraX-Personal-Project.git
cd StrikeTraX-Personal-Project
npm install
cd backend
uv sync
```

Copy each .env.example to a .env file in the same directory, and fill them with real values:
- Root .env - VITE_API_URL
- Backend .env - DB fields and FRONTEND_ORIGIN

Then, create the game table in the database:

```sh
uv run python create_tables.py
```

Run the following, from two different terminals:

Terminal 1, from backend/
```sh
uv run fastapi dev main.py
```

Terminal 2, from repo root
```sh
npm run dev
```

## Notable Design Decisions

* Phase 2 of this project added a database with Azure SQL. This allows games to be saved in a stored database.
* Until Phase 4 is done, a session ID is generated or retrieved by the client to be sent to the database, and is used to retrieve only the user's games.
* History is currently unbounded, you could enter a hundred games, but given the current scale of the application I felt like pagination was fine to set aside for now.
* Currently, corrupted or invalid partial game data is simply discarded, this should be essentially impossible to do without directly messing with devtools, so this is fine for partial games.
* Invalid games that are sent to the database are detected and refused. This includes invalid values, out of bound numbers, and a final score that doesn't match the backend's calculation.
* History page detects and flags corrupted games from API responses and hides them. This realistically should only happen with response tampering, but if for some reason the database holds invalid info it will hide that game.
* History page will display an error message if the response data itself is corrupted.

## Roadmap

Remaining phases to be completed:

### Phase 3

* Sorting options on History page, oldest-newest, newest-oldest, high-low, low-high
* Date filtering on History page, pick two dates and see all games between them
* Add editing to the game in progress, right now you have to finish the game and choose to not keep it, bad UX
* Potentially add editing saved games to History page

### Phase 4

* Add login UI and remove placeholder anonymous session ID
* Use passlib/bcrypt to hash passwords and JWT tokens for sessions
* Update DB schema and POST/GET to use userID instead of anonymous session ID
