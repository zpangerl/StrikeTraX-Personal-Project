"""Setup for connecting to the Azure database."""

from sqlalchemy import URL, create_engine

from settings import Settings

# Also imported by main.py to access environment variables.
settings = Settings()

connection_url = URL.create(
    "mssql+pyodbc",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_server,
    database=settings.db_name,
    # Azure SQL requires encrypted connections.
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "Encrypt": "yes"
    },
)

# Azure can drop idle connections, I believe pool_pre_ping helps with that.
engine = create_engine(connection_url, pool_pre_ping=True)