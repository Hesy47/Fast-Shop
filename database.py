from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")

engin = create_engine(database_url, echo=True)
local_session = sessionmaker(bind=engin, autoflush=False)

db_base = declarative_base()
