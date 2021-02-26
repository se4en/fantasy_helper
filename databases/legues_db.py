import sqlite3
import functools
import datetime
import requests
from bs4 import BeautifulSoup
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text, bold, italic, code, pre

class LegueDB():
    """
    Include table in db for one legue
    """
    def __init__(self, legue_name, fonbet_url, sports_url, repr_name=None):
        self.legue_name = legue_name
        self.repr_name = repr_name
        self.fonbet_url = fonbet_url
        self.sports_url = sports_url
        self.games_count = 0
        self.deadline = datetime.datetime.now()
        self.teams = []
        self.coefs = []
        self.conn = sqlite3.connect("legues.db", check_same_thread = False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + legue_name + '''
                    (team_name text, team_vs_name text, coef_for real, coef_against real)
                ''')    

    def __str__(self):
        return emojize(LegueDB.emojize_name(self.legue_name) + " " + self.repr_name)

    @staticmethod
    def emojize_name(country_name):
        emoji_dict = {
            "Russia" : "🇷🇺",
            "France" : "🇫🇷",
            "England" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Championship" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Turckey" : "🇹🇷",
            "Portugal" : "🇵🇹",
            "Netherlands" : "🇳🇱",
            "Italy" : "🇮🇹",
            "UEFA_1" : "🇪🇺",
            "UEFA_2" : "🇪🇺",
            "Spain" : "🇪🇸",
            "Germany" : "🇩🇪"
        }
        return emoji_dict[country_name]

    def get_name(self):
        return self.legue_name

    def __transform_deadline(self, new_deadline):
        day, month_time = new_deadline.split(' ')
        month, time = month_time.split('|')

        day = int(day)
        month = {
            "января" : 1,
            "февраля" : 2,
            "марта" : 3,
            "апреля" : 4,
            "мая" : 5,
            "июня" : 6,
            "июля" : 7,
            "августа" : 8,
            "сентября" : 9,
            "октября" : 10,
            "ноября" : 11,
            "декабря" : 12
        }[month]
        hour, minute = list(map(int, time.split(":")))
        return datetime.datetime(datetime.datetime.now().year, month, day, hour, minute)

    def __try_update_deadline(self):
        if datetime.datetime.now() < self.deadline:
            return False
        response = requests.get("https://www.sports.ru/fantasy/football/team/points/2284228.html")
        soup = BeautifulSoup(response.text, 'lxml')
        buf = soup.find("div", {"class": "pageLayout"}).find("div", {"class": "tabs-container mB20"})
        new_deadline = buf.find_all("table", {"class": "profile-table"})[0].find_all("tr")[1].find("td")
        self.deadline = self.__transform_deadline(new_deadline)
        return True

    def update_match_name(self, match_name):
        """
        Return list with pair of team names
        """
        teams = match_name.split(' — ')
        return teams

    def update_match_coefs(self, match_link):
        """
        Return list of lists with pairs of team coefss, like
        [ [coef1_for, coef1_ag], [coef2_for, coef2_ag]] 
        """
        if not match_link:
            return False
        coef_1.append(float(for_coefs_1.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[1].text))
        coef_1.append(float(against_coef.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[2].text))
        coef_2.append(float(for_coefs_2.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[1].text))
        coef_2.append(float(against_coef.find_elements_by_class_name('table__grid-row')[1].find_elements_by_tag_name('td')[2].text))
        return [coef_1, coef_2]

    def update_coefs(self):
        """
        Update self.teams and self.coefs
        """
        self.coefs = [] # list of pairs of coefs
        self.teams = [] # list of teams' names
        for i in range(len(table_rows)-2):
            self.coefs += self.update_match_coefs(
                table_rows[i+1].find_element_by_class_name('table__match-title-text').get_attribute("href")
                )
            self.teams += self.update_match_name(
                table_rows[i+1].find_element_by_class_name('table__match-title-text').text
                )
        if self.update_match_coefs(
            table_rows[i+2].find_element_by_class_name('table__match-title-text').get_attribute("href")
            ):  
            self.coefs += self.update_match_coefs(
                table_rows[i+2].find_element_by_class_name('table__match-title-text').get_attribute("href")
                )
            self.teams += self.update_match_name(
                table_rows[i+2].find_element_by_class_name('table__match-title-text').text
                )

    def update_db(self):
        """
        Rewrite teams and coefs in db
        """
        self.update_coefs()
        # clear table
        self.cursor.execute('DELETE FROM ' + self.legue_name)
        # colect insert data
        print(self.teams, self.coefs)
        insert_data = []
        for i in range(0,len(self.teams),2):
            insert_data.append( (self.teams[i] + ' [д]', self.teams[i+1], self.coefs[i][0], self.coefs[i][1]) )
            insert_data.append( (self.teams[i+1] + ' [г]', self.teams[i], self.coefs[i+1][0], self.coefs[i+1][1]) )
        # insert data to db
        self.cursor.executemany('INSERT INTO ' + self.legue_name + ' VALUES (?,?,?,?)', insert_data)    
        self.conn.commit()

    def try_update_games_count(self):


    def get_coefs(self):
        """
            Return message to user
        """
        self.cursor.execute('SELECT * FROM ' + self.legue_name)
        all_coefs = self.cursor.fetchall()
        all_coefs.sort(key=lambda line: line[2])
        result = ["\U0001F5E1 Атакующий потенциал:\n",]
        result += list(map(functools.partial(self.__trsansform_coefs, type="for"), all_coefs))
        result += ["\n\U0001F6E1 Защитный потенциал:\n"]
        all_coefs.sort(key=lambda line: line[3])
        result += list(map(functools.partial(self.__trsansform_coefs, type="against"), all_coefs))
        return ('\n').join(result)

    def __trsansform_coefs(self, db_tup, type="for"):
        """
        Transform row from db to string line
        """
        if type=="for":
            coef = emojize(self.__emojize_coef(db_tup[2]) + " " + str(db_tup[2]) + "  " if len(str(db_tup[2]))==4 
                           else self.__emojize_coef(db_tup[2]) + " " + str(db_tup[2]) + "0" + "  ")
        else:
            coef = emojize(self.__emojize_coef(db_tup[3]) + " " + str(db_tup[3]) + "  " if len(str(db_tup[3]))==4 
                           else self.__emojize_coef(db_tup[3]) + " " + str(db_tup[3]) + "0" + "  ")
        team1_max_len = 8
        if len(db_tup[0])<=team1_max_len + 4:
            team1 = f"<b>{db_tup[0]} </b>"
        else:
            team1 = f"<b>{db_tup[0][:team1_max_len]} {db_tup[0].split()[-1]} </b>"
        team2_max_len = 8
        if len(db_tup[1])<=team2_max_len:
            team2 = f"<i>vs {db_tup[1]}</i>"
        else:
            team2 = f"<i>vs {db_tup[1][:team2_max_len]}</i>"
        return text(coef, team1, team2, sep="")

    def __emojize_coef(self, coef):
        """
        Return emoji to coef
        """
        if coef<=1.5:
            return "🟩"
        elif coef<=2.0:
            return "🟨"
        elif coef<=3.0:
            return "🟧"
        else:
            return "🟥"