from typing import Annotated as typingAnnotated

from fastapi import Depends
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import settings

engine = create_engine(
    url=settings.database_url,
    echo=settings.SQL_ALCHEMY_DEBUG,
    pool_size=10,
    max_overflow=10
)

session_factory = sessionmaker(bind=engine)

Str256 = typingAnnotated[str, String(256)]

Str2048 = typingAnnotated[str, String(2048)]

class Base(DeclarativeBase):
    type_annotation_map = {
        Str256: String(256),
        Str2048: String(2048)
    }

# Generator to get a session from the session factory
# todo
def get_db() -> Session:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

db_dependency = typingAnnotated[Session, Depends(get_db)]
