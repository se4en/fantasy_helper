import logging
import os
import sys

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from loader import bot
from db.models.media import Media
from db.database import Session

from fantasy_helper.conf.config import ADMINS


class MediaDao:
    def __init__(self, path: str) -> None:
        # STATS_DATA_PATH
        self.__path: str = path

    async def upload_files(self, league_name: str, stat_type: str) -> bool:
        # method = bot.send_photo,
        # file_attr = 'photo'
        try:
            # create paths
            league_path = os.path.join(self.__path, league_name)
            if not os.path.exists(league_path):
                return False
            stat_path = os.path.join(league_path, stat_type)
            if not os.path.exists(stat_path):
                return False

            last_3_path = os.path.join(stat_path, "last_3.png")
            last_5_path = os.path.join(stat_path, "last_5.png")

            result = await self.upload_file(last_3_path, league_name, stat_type, False)
            result &= await self.upload_file(last_5_path, league_name, stat_type, True)
            return result
        except:
            return False

    @staticmethod
    async def upload_file(
        file_path: str, league_name: str, stat_type: str, last_5: bool
    ) -> bool:
        session: SQLSession = Session()
        try:
            with open(file_path, "rb") as file:
                msg = await bot.send_photo(ADMINS[0], file, disable_notification=True)
                file_id = msg.photo[-1].file_id

                session.query(Media).filter(
                    and_(
                        Media.league == league_name,
                        Media.stat_type == stat_type,
                        Media.last_5 == last_5,
                    )
                ).delete()
                session.add(Media(league_name, stat_type, last_5, file_id, file_path))
                return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()
