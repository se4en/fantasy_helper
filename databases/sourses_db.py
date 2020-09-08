import sqlite3
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, italic

class Sourses:
    def __init__(self):
        self.conn = sqlite3.connect("sourses.db", check_same_thread = False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sourses
            (legue_name text, repr_name, link text, discription text)
        """)

    @staticmethod
    def emojize_name(country_name):
        emoji_dict = {
            "Russia" : "🇷🇺",
            "France" : "🇫🇷",
            "England" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Championship" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
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

    @staticmethod
    def unrepresent_name(repr_name):
        name_dict = {
            "РПЛ" : "Russia",
            "АПЛ" : "England",
            "Лига 1" : "France",
            "ЛаЛига" : "Spain",
            "Чемпионшип" : "Championship",
            "Эрдевизи" : "Netherlands",
            "Бундеслига" : "Germany",
            "Суперлига" : "Turkey",
        }
        return name_dict[repr_name]

    @staticmethod
    def represent_name(name):
        name_dict = {
            "Russia" : "РПЛ",
            "England" : "АПЛ",
            "France" : "Лига 1",
            "Spain" : "ЛаЛига",
            "Championship" : "Чемпионшип",
            "Netherlands" : "Эрдевизи",
            "Germany" : "Бундеслига",
            "Turkey" : "Суперлига",
        }
        return Sourses.emojize_name(name) + " " + name_dict[name]

    def add_sourse(self, legue_name, repr_name, link, discription):
        self.cursor.execute("INSERT INTO sourses VALUES (?,?,?,?)", 
            (legue_name, repr_name, link, discription)
        )
        self.conn.commit()

    def delete_sourse(self, link):
        self.cursor.execute("DELETE FROM sourses WHERE link = ? ", link)
        self.conn.commit()

    def get_legues(self):
        self.cursor.execute("SELECT DISTINCT legue_name FROM sourses")
        return self.cursor.fetchall()

    def get_sourses(self, legue_name):
        self.cursor.execute("""
            SELECT * FROM sourses
            WHERE legue_name = ?
        """, (legue_name,))
        sourses = self.cursor.fetchall()
        return self.__transform_sourses(sourses)

    def __transform_sourses(self, sourses_list):
        result = []
        for i in range(len(sourses_list)):
            result += [emojize(self.emojize_number(i+1)) + " " + 
            sourses_list[i][2] + "\n" + italic(sourses_list[i][3])]
        return ('\n').join(result)