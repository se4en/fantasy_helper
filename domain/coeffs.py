from domain.manager import Manager
from db.parse.xbet import XBet
from db.parse.sports import Sports


class CoeffManager(Manager):

    def __init__(self, xbet: XBet, sports: Sports):
        self.xbet = xbet
        self.sports = sports
