import os
import sys
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from loader import bot
from data.config import admins
from db.models.media_ids import MediaIds
from db.database import Session


async def upload_files(base_path: str, league_name: str, stat_type: str) -> bool:
    # method = bot.send_photo,
    # file_attr = 'photo'
    try:
        # create paths
        league_path = os.path.join(base_path, league_name)
        if not os.path.exists(league_path):
            return False
        stat_path = os.path.join(league_path, stat_type)
        if not os.path.exists(stat_path):
            return False

        last_3_path = os.path.join(stat_path, "last_3.png")
        last_5_path = os.path.join(stat_path, "last_5.png")

        result = await upload_file(last_3_path, league_name, stat_type)
        result *= await upload_file(last_5_path, league_name, stat_type)
        return result
    except:
        return False


async def upload_file(file_path: str, league_name: str, stat_type: str) -> bool:
    try:
        with open(file_path, 'rb') as file:
            msg = await bot.send_photo(admins[0], file, disable_notification=True)
            file_id = msg.photo[-1].file_id

            session: SQLSession = Session()
            session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                MediaIds.stat_type == stat_type)).delete()
            session.add(MediaIds(league_name, stat_type, file_id, file_path))
            return True
    except Exception as ex:
        # TODO logging
        print(ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return False
    finally:
        session.commit()
        session.close()
