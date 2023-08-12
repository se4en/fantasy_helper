from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from fantasy_helper.conf.config import DATABASE_URI


db_engine = create_engine(DATABASE_URI)
if not database_exists(db_engine.url):
    create_database(db_engine.url)

Session = sessionmaker(bind=db_engine)
Base = declarative_base()
