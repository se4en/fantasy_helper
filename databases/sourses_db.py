import sqlite3

class Sourses:
    def __init__(self, legue_name, repr_name=None):
        self.legue_name = legue_name
        self.repr_name = repr_name
        self.conn = sqlite3.connect("legues.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sourses
            (legue_name text, link text, discription text)
        """)    

    def get_name(self):
        return self.legue_name

    @staticmethod
    def emojize_name(country_name):
        emoji_dict = {
            "Russia" : "🇷🇺",
            "France" : "🇫🇷",
            "England" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Turkey" : "🇹🇷",
            "Portugal" : "🇵🇹",
            "Netherlands" : "🇳🇱",
            "Italy" : "🇮🇹",
            "Europe" : "🇪🇺",
            "Spain" : "🇪🇸",
            "Germany" : "🇩🇪"
        }
        return emoji_dict[country_name]

    @staticmethod
    def emojize_number(number):
        emoji_dict = {
            1 : ":one:",
            2 : ":two:",
            3 : ":three:",
            4 : ":four:",
            5 : ":five:",
            6 : ":six:",
            7 : ":seven:",
            8 : ":eight:",
            9 : ":nine:",
            10 : "\U0001F51F"
        }
        return emoji_dict[number]

    def __str__(self):
        return self.emojize_name(self.legue_name) + " " + self.repr_name

    def add_sourse(self, legue_name, link, discription):
        self.cursor.execute("INSERT INTO sourses VALUES (?,?,?)", 
            (legue_name, link, discription)
        )
        self.conn.commit()

    def get_sourses(self, legue_name):
        self.cursor.execute("""
            SELECT * FROM sourses
            WHERE legue_name = ?
        """, legue_name)
        sourses = self.cursor.fetchall()
        return self.__transform_sourses(sourses)

    def __transform_sourses(self, sourses_list):
        for i in 
