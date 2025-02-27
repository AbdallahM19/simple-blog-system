"""/app/database.py"""

import os
from sqlmodel import SQLModel, Session, create_engine

sqlite_file_name = "database.db"

engine = create_engine(
    url=f"sqlite:///{sqlite_file_name}",
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def delete_db():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
        print("Database deleted successfully.")
    else:
        print("Database file does not exist.")
