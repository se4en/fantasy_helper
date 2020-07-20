import sqlite3
from selenium import webdriver

class LegueDB():
    def __init__(self, legue_name, fonbet_url):
        self.legue_name = legue_name
        self.fonbet_url = fonbet_url
        self.conn = sqlite3.connect("legues.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + legue_name + '''
                    (player_id integer, name text, amplua integer, 
                    team text, price real, old_popularity integer, 
                    new_popularity_1 integer, new_popularity_2 integer, rating integer)
                ''')