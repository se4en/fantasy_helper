from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, Float

from db.database import Base


class Coeff(Base):
    __tablename__ = 'coeffs'

    id = Column(Integer, primary_key=True)
    team = Column(String, nullable=False)
    team_against = Column(String, nullable=False)
    league = Column(String, nullable=False)
    more_1_5 = Column(Float, nullable=False)
    clean_sheet = Column(Float, nullable=False)
    is_home = Column(Boolean, nullable=False)
    is_cur_round = Column(Boolean, nullable=False)

    def __init__(self, team: str, team_against: str, league: str,
                 more_1_5: float, clean_sheet: float, is_home: bool, is_cur_round: bool):
        self.team = team
        self.team_against = team_against
        self.league = league
        self.more_1_5 = more_1_5
        self.clean_sheet = clean_sheet
        self.is_home = is_home
        self.is_cur_round = is_cur_round

    def __repr__(self):
        if self.is_home:
            result: str = f"{self.team} vs {self.team_against} "
        else:
            result: str = f"{self.team_against} vs {self.team} "

        result += f"tm={self.more_1_5} cs={self.clean_sheet} cur_round={self.is_cur_round}"
        return result
