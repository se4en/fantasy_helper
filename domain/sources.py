import os
import sys
import logging
from datetime import datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from domain.manager import Manager
from db.models.sources import Source
from db.database import Session
from db.models.leagues_info import League_info


class SourcesManager(Manager):

    def __init__(self):
        super().__init__()

    def add_source(self, name: str, league_name: str, url: str, description: str) -> bool:
        logging.info(f"Add source {name} for league={league_name}")

        session: SQLSession = Session()
        try:
            session.add(Source(name, league_name, url, description))
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    def delete_source(self, name: str, league_name: str, url: str) -> bool:
        logging.info(f"Delete source {name} for league={league_name}")

        session: SQLSession = Session()
        try:
            session.query(Source).filter(and_(Source.league == league_name, Source.name == name,
                                              Source.url == url)).delete()
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    def delete_source_by_id(self, source_id: int) -> str:
        logging.info(f"Delete source with id={source_id}")

        session: SQLSession = Session()
        try:
            league_name = session.query(Source).filter(and_(Source.id == source_id)).first().league
            session.query(Source).filter(and_(Source.id == source_id)).delete()
            return league_name
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.commit()
            session.close()

    def get_sources_repr(self, league_name: str) -> str:
        session: SQLSession = Session()
        try:
            sources = session.query(Source).filter(Source.league == league_name).all()
            return self.__transform_sources(sources)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()

    def get_sources(self, league_name: str) -> List[Source]:
        session: SQLSession = Session()
        try:
            sources = session.query(Source).filter(Source.league == league_name).all()
            return sources
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return []
        finally:
            session.close()

    def __transform_sources(self, sources: List[Source]) -> str:
        if not sources:
            return "Источников нет("
        result = []
        for source in sources:
            result.append(f"Name={source.name} url={source.url}")
        return '\n'.join(result)
