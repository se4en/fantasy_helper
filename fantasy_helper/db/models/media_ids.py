from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean

from db.database import Base


class MediaIds(Base):
    __tablename__ = 'media_ids'

    id = Column(Integer, primary_key=True)
    league = Column(String, nullable=False)
    stat_type = Column(String, nullable=False)
    last_5 = Column(Boolean, nullable=False)
    file_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)

    def __init__(self, league: str, stat_type: str, last_5: bool, file_id: str, filename: str):
        self.league = league
        self.stat_type = stat_type
        self.last_5 = last_5
        self.file_id = file_id
        self.filename = filename

    def __repr__(self):
        return f"Filename={self.filename} id={self.file_id}"
