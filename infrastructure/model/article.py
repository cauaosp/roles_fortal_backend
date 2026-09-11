from datetime import datetime

from infrastructure.database import Base
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    String,
)


class Article(Base):
    __tablename__ = "articles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    subtitle = Column(String)
    author = Column(String)
    publication_date = Column(DateTime)
    link = Column(String, unique=True, nullable=False)
    journal = Column(String, nullable=False)
    category = Column(JSON)
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
