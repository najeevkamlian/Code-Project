from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pymongo import MongoClient
from app.config import get_settings


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session():
    with Session(get_engine()) as session:
        yield session


@lru_cache
def get_mongo():
    return MongoClient(get_settings().mongodb_url, serverSelectionTimeoutMS=3000)


def get_audit_collection():
    return get_mongo()[get_settings().mongodb_database].audit_events
