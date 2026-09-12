from infrastructure.database import Base
from sqlalchemy import JSON, BigInteger, Column, DateTime, Identity, String, func


class Article(Base):
    __tablename__ = "articles"

    id = Column(BigInteger, Identity(), primary_key=True)
    title = Column(String, nullable=False)
    subtitle = Column(String)
    author = Column(String)
    publication_date = Column(DateTime)
    link = Column(String, unique=True, nullable=False)
    journal = Column(String, nullable=False)
    category = Column(JSON)
    scraped_at = Column(DateTime)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
