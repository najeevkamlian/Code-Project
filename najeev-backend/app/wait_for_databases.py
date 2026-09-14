import time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from app.database import get_engine, get_mongo


def wait_for_databases():
    for attempt in range(60):
        try:
            with get_engine().connect() as connection:
                connection.execute(text('SELECT 1'))
            get_mongo().admin.command('ping')
            print('PostgreSQL and MongoDB are ready.')
            return
        except (SQLAlchemyError, PyMongoError):
            if attempt == 59:
                raise
            time.sleep(2)


if __name__ == '__main__':
    wait_for_databases()
