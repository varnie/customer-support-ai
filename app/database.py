import os

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import Config

DATABASE_URL = Config.DATABASE_URL

async_engine = create_async_engine(DATABASE_URL, echo=os.environ.get('SQLALCHEMY_ECHO', False) == 'true',  poolclass=NullPool)

# noinspection PyTypeChecker
AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=async_engine,
    class_=AsyncSession
)
