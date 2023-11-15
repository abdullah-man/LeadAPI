from sqlmodel import SQLModel, Session, create_engine
from decouple import config

DB_USERNAME = config('DB_USERNAME')
DB_PASS = config('DB_PASS')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')


database_connection_string = f"postgresql://{DB_USERNAME}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# database_connection_string = f"postgresql://postgres:axiom123@localhost:5432/postgres"
connect_args = {"check_same_thread" : False}

# an instance of the created SQL database 
engine_url = create_engine(database_connection_string, echo=True)


def conn():
    # Create a Database and as well as the table present in the file: events
    SQLModel.metadata.create_all(engine_url)

def get_session():
    # to persist the session in our application this function works
    with Session(engine_url) as session:
        yield session

