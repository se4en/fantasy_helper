import asyncio
from typing import List
import os.path as path
import datetime
import sys

from loguru import logger

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.utils.create_db import create_db


async def main():
    create_db()
    
    logger.info(f"Start update coeffs")
    dao = CoeffDAO()
    await dao.update_coeffs_all_leagues()
    dao.update_feature_store()
    logger.info(f"Finish update coeffs")


if __name__ == "__main__":
    asyncio.run(main())
