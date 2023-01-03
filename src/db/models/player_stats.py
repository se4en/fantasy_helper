from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, Float

from db.database import Base


class PlayerStats(Base):
    __tablename__ = 'player_stats'

    # player info
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    league = Column(String, nullable=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=False)
    goals = Column(Integer, default=0)
    # shoots
    last3_shoots_per_game = Column(Float, default=0.0)
    last3_on_target_per_shoot = Column(Float, default=0.0)
    last5_shoots_per_game = Column(Float, default=0.0)
    last5_on_target_per_shoot = Column(Float, default=0.0)
    # xg
    last3_xg_per_game = Column(Float, default=0.0)
    last3_npxg_per_game = Column(Float, default=0.0)
    last3_xa_per_game = Column(Float, default=0.0)
    last5_xg_per_game = Column(Float, default=0.0)
    last5_npxg_per_game = Column(Float, default=0.0)
    last5_xa_per_game = Column(Float, default=0.0)
    # shoots creation
    last3_sca_per_game = Column(Float, default=0.0)
    last3_gca_per_game = Column(Float, default=0.0)
    last5_sca_per_game = Column(Float, default=0.0)
    last5_gca_per_game = Column(Float, default=0.0)
    # stats
    # after round 0
    r0_minutes = Column(Float, default=0.0)
    r0_shoots = Column(Integer, default=0)
    r0_shoots_on_target = Column(Integer, default=0)
    r0_xg = Column(Float, default=0.0)
    r0_npxg = Column(Float, default=0)
    r0_xa = Column(Float, default=0)
    r0_sca = Column(Integer, default=0.0)
    r0_gca = Column(Integer, default=0)
    # round 1
    r1_minutes = Column(Float, default=0.0)
    r1_shoots = Column(Integer, default=0)
    r1_shoots_on_target = Column(Integer, default=0)
    r1_xg = Column(Float, default=0.0)
    r1_npxg = Column(Float, default=0)
    r1_xa = Column(Float, default=0)
    r1_sca = Column(Integer, default=0.0)
    r1_gca = Column(Integer, default=0)
    # round 2
    r2_minutes = Column(Float, default=0.0)
    r2_shoots = Column(Integer, default=0)
    r2_shoots_on_target = Column(Integer, default=0)
    r2_xg = Column(Float, default=0.0)
    r2_npxg = Column(Float, default=0)
    r2_xa = Column(Float, default=0)
    r2_sca = Column(Integer, default=0.0)
    r2_gca = Column(Integer, default=0)
    # round 3
    r3_minutes = Column(Float, default=0.0)
    r3_shoots = Column(Integer, default=0)
    r3_shoots_on_target = Column(Integer, default=0)
    r3_xg = Column(Float, default=0.0)
    r3_npxg = Column(Float, default=0)
    r3_xa = Column(Float, default=0)
    r3_sca = Column(Integer, default=0.0)
    r3_gca = Column(Integer, default=0)
    # round 4
    r4_minutes = Column(Float, default=0.0)
    r4_shoots = Column(Integer, default=0)
    r4_shoots_on_target = Column(Integer, default=0)
    r4_xg = Column(Float, default=0.0)
    r4_npxg = Column(Float, default=0)
    r4_xa = Column(Float, default=0)
    r4_sca = Column(Integer, default=0.0)
    r4_gca = Column(Integer, default=0)
    # round 5
    r5_minutes = Column(Float, default=0.0)
    r5_shoots = Column(Integer, default=0)
    r5_shoots_on_target = Column(Integer, default=0)
    r5_xg = Column(Float, default=0.0)
    r5_npxg = Column(Float, default=0)
    r5_xa = Column(Float, default=0)
    r5_sca = Column(Integer, default=0.0)
    r5_gca = Column(Integer, default=0)

    def __init__(self, name: str, league: str, team: str, position: str):
        self.name = name
        self.league = league
        self.team = team
        self.position = position

    def __repr__(self):
        return f"Name={self.name} team={self.team} pos={self.position}"
