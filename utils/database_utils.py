from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


master_engine = None


def get_master_engine():
    """get_master_engine."""
    global master_engine

    if not master_engine:
        master_engine = create_engine(
            "postgresql+psycopg2://cyueqonebgcvcq:739b3a6ef7e44f3f8483add96f25b14c7a62692192e90513ce848926160033c0@ec2-35-168-145-180.compute-1.amazonaws.com:5432/danch95tg7ijgl",
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
