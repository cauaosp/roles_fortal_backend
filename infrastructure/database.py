import os

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise ValueError("❌ DB_URL não configurada no .env")

engine = create_engine(
    DB_URL.replace("postgresql://", "postgresql+psycopg://"),
    poolclass=NullPool,
)


class Base(DeclarativeBase):
    pass
