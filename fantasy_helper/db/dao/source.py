import os
import sys
import logging
import typing as t

from aiogram.utils.emoji import emojize
from sqlalchemy import and_

from fantasy_helper.db.models.source import Source
from fantasy_helper.db.database import Session
from fantasy_helper.utils.prettify import emojize_number


class SourceDao:
    def __init__(self):
        pass

    def add_source(
        self, name: str, league_name: str, url: str, description: str
    ) -> bool:
        logging.info(f"Add source {name} for league={league_name}")
        session = None
        try:
            session = Session()
            session.add(Source(name, league_name, url, description))
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            if session is not None:
                session.commit()
                session.close()

    def delete_source(self, name: str, league_name: str, url: str) -> bool:
        logging.info(f"Delete source {name} for league={league_name}")
        session = None
        try:
            session = Session()
            session.query(Source).filter(
                and_(
                    Source.league == league_name, Source.name == name, Source.url == url
                )
            ).delete()
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            if session is not None:
                session.commit()
                session.close()

    def delete_source_by_id(self, source_id: int) -> str:
        logging.info(f"Delete source with id={source_id}")
        session = None
        try:
            session = Session()
            league_name = (
                session.query(Source)
                .filter(and_(Source.id == source_id))
                .first()
                .league
            )
            session.query(Source).filter(and_(Source.id == source_id)).delete()
            return league_name
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            if session is not None:
                session.commit()
                session.close()

    def get_sources_repr(self, league_name: str) -> str:
        session = None
        try:
            session = Session()
            sources = session.query(Source).filter(Source.league == league_name).all()
            return emojize(self.__transform_sources(sources))
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            if session is not None:
                session.close()

    def get_sources(self, league_name: str) -> t.List[Source]:
        session = None
        try:
            session = Session()
            sources = session.query(Source).filter(Source.league == league_name).all()
            return sources
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return []
        finally:
            if session is not None:
                session.close()

    def __transform_sources(self, sources: t.List[Source]) -> str:
        if not sources:
            return "Источников нет("

        result = [":card_index_dividers: Доступные источники:\n"]
        result += [
            emojize_number(i + 1) + f" [{s.name}]({s.url})\n_{s.description}_\n"
            for i, s in enumerate(sources)
        ]
        return "\n".join(result)
