import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


master_engine = None

db = os.environ.get("DATABASE_URL")

def get_master_engine():
    """get_master_engine."""
    global master_engine

    if not master_engine:
        master_engine = create_engine(
            db,
            pool_recycle=3600,
            pool_size=10,
            pool_timeout=1,
            echo=False,
            max_overflow=5,
            convert_unicode=True,
            client_encoding="utf8",
        )
    return master_engine


def get_db_session():
    sesion_factory = scoped_session(sessionmaker(bind=get_master_engine()))
    return sesion_factory()


def get_connection():
    engine = get_master_engine()
    return engine.connect()
