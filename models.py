from sqlalchemy import Column, BigInteger, String
from database import db_base


class Collection(db_base):
    __tablename__ = "collections"
    id = Column(BigInteger, primary_key=True, nullable=False)
    title = Column(String(35), nullable=False)
