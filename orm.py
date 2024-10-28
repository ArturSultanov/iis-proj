from sqlalchemy import text, insert
from database import session_factory, engine
from db_models import Base, UsersOrm


def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def insert_data():
    kirill = UsersOrm(username="kirill", password="kir123!1")
    artur = UsersOrm(username="artur", password="art123!1")
    with session_factory() as session:
        session.add_all([kirill, artur])
        session.commit()


create_tables()
insert_data()