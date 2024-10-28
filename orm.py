from sqlalchemy import text, insert
from database import session_factory, engine
from db_models import Base, UsersOrm


def create_tables():
    Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)