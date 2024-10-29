from typing import Annotated as typingAnnotated, Annotated
from sqlalchemy.sql.annotation import Annotated as sqlAnnotated

from fastapi import Depends
from sqlalchemy import create_engine, text, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from config import settings

engine = create_engine(
    url=settings.database_url,
    echo=True,
    pool_size=10,
    max_overflow=10
)

session_factory = sessionmaker(bind=engine)

Str256 = Annotated[str, String(256)]

Str2048 = Annotated[str, String(2048)]

class Base(DeclarativeBase):
    type_annotation_map = {
        Str256: String(256),
        Str2048: String(2048)
    }

def get_db() -> Session:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

db_dependency = typingAnnotated[Session, Depends(get_db)]


# with engine.connect() as conn:
#     res = conn.execute(text("SELECT VERSION()"))
#     print(f"{res.first()=}")
