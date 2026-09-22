"""Create database tables, will not overwrite existing tables. Run manually."""

from database import engine
from models import Base

Base.metadata.create_all(engine)