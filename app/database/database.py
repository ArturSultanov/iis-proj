from typing import Annotated as typingAnnotated, Iterable, Generator

from fastapi import Depends
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import settings

# Database engine
engine = create_engine(
    url=settings.database_url,
    echo=settings.SQL_ALCHEMY_DEBUG,
    pool_size=10,
    max_overflow=10
)

# Session factory for the database
session_factory = sessionmaker(bind=engine)

# String annotations for MySQL to use as column types
Str256 = typingAnnotated[str, String(256)]
Str2048 = typingAnnotated[str, String(2048)]

class Base(DeclarativeBase):
    type_annotation_map = {
        Str256: String(256),
        Str2048: String(2048)
    }

# Function to create all tables in the database if they do not exist
def create_all_tables():
    Base.metadata.create_all(engine)

# Database connection generator
def get_db() -> Generator[Session, None, None]:
    db = session_factory()
    try:
        # yield the database session
        yield db
    finally:
        # close used the database session
        db.close()

# Dependency to get the database session in the routers
db_dependency = typingAnnotated[Session, Depends(get_db)]
