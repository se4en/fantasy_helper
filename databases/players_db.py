import sqlite3
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold
import requests
from bs4 import BeautifulSoup

class PlayersDB:
    def __init__(self, legue_name, legue_url, repr_name=None):
        self.legue_name = legue_name
        self.legue_url = legue_url
        self.repr_name = repr_name
        self.popular_list = []
        self.conn = sqlite3.connect("players.db", check_same_thread = False)
        self.cursor = self.conn.cursor()
        # https://www.sports.ru/fantasy/football/tournament/49.html
        split_url = self.legue_url.split('/')
        # https://www.sports.ru/fantasy/football/tournament/ratings/popular/49.html
        self.popular_players_url = '/'.join(split_url[0:-1]) + '/ratings/popular/' + split_url[-1]

    def get_name(self):
        return self.legue_name

    def __str__(self):
        return self.emojize_name(self.legue_name) + " " + self.repr_name

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

    def __update_popular_list(self):
        self.cursor.execute('SELECT * FROM ' + self.legue_name + """
            ORDER BY dif_popularity DESC
            LIMIT 10
        """)
        best_players = self.cursor.fetchall()
        self.cursor.execute('SELECT * FROM ' + self.legue_name + """
            ORDER BY dif_popularity 
            LIMIT 10
        """)
        whorst_players = self.cursor.fetchall()
        self.popular_list = ["\U0001F4C8 Популярные игроки:\n"]
        self.popular_list += self.__transform_players(best_players)
        self.popular_list += ["\n\U0001F4C9 Непопулярные игроки:\n"]
        self.popular_list += self.__transform_players(whorst_players)

    def __transform_players(self, players_list):
        result = []
        for i in range(len(players_list)):
            if players_list[i][4]<0:
                result += [emojize(f"{self.emojize_number(i+1)} {players_list[i][4]}" +
                           bold(f" {players_list[i][0]}"))]
            else:
                result += [emojize(f"{self.emojize_number(i+1)} +{players_list[i][4]}" +
                           bold(f" {players_list[i][0]}"))]
        return result

    def get_popular(self):
        self.__update_popular_list()
        return ("\n").join(self.popular_list)
        
    def create_db(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.legue_name + '''
                    (first_name text, team text, amplua integer, 
                    new_popularity integer, dif_popularity integer)
                ''')
        self.cursor.execute("DELETE FROM " + self.legue_name)
        self.conn.commit()
        self.create_page(self.popular_players_url)
        j = 2
        while self.create_page(self.popular_players_url + '?p=' + str(j)):
            j = j + 1

    def create_page(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        players = soup.find_all("tr")
        for i in range(len(players) - 1):
            player_population = int(players[i+1].find_all("td")[-1].text)
            player_info = players[i+1].find("div", {"class": "overBox"}).text.split("\n")
            player_name = player_info[1]
            player_amplua = player_info[2]
            player_team = player_info[3]
            self.__add_player(player_name, player_amplua, player_population, player_team)
        if len(players) < 51:
            return False
        return True

    def __add_player(self, player_name, player_amplua, player_population, player_team):
        self.cursor.execute("INSERT INTO " + self.legue_name + " VALUES (?,?,?,?,?)", 
            (player_name, player_team, player_amplua, player_population, 0)
        )
        self.conn.commit()

    def update_db(self, new_round=False):
        self.cursor.execute(f"UPDATE {self.legue_name} SET dif_popularity = 0")
        self.conn.commit()
        self.update_page(self.popular_players_url, new_round)
        j = 2
        while self.update_page(self.popular_players_url + '?p=' + str(j), new_round):
            j = j + 1

    def update_page(self, url, new_round):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        players = soup.find_all("tr")
        for i in range(len(players)-1):
            player_name = players[i+1].find("a").text
            new_population = int(players[i+1].find_all("td")[-1].text)
            # update row in db
            if not self.__update_player(player_name, new_population, new_round):
                player_info = players[i+1].find("div", {"class": "overBox"}).text.split("\n")
                player_amplua = player_info[2]
                player_team = player_info[3]
                self.__add_player(player_name, player_amplua, new_population, player_team)
        if len(players) < 51:
            return False
        return True

    def __update_player(self, player_name, new_popularity, new_round):
        self.cursor.execute("SELECT * FROM " + self.legue_name + """
            WHERE first_name = ?
        """, (player_name, )) 
        player_data = self.cursor.fetchone()
        try:
            if not player_data:
                return False
            elif player_data==[]:
                return False
            else:
                if new_round:
                    self.cursor.execute("UPDATE " + self.legue_name + """
                        SET new_popularity = ? ,
                            dif_popularity = ?
                        WHERE first_name = ?
                    """, 
                    (new_popularity, 0, player_name))
                else:
                    self.cursor.execute("UPDATE " + self.legue_name + """
                        SET dif_popularity = ?
                        WHERE first_name = ?
                    """, 
                    (new_popularity - player_data[3], player_name))
                self.conn.commit()
                return True
        except:
            return False

    def look_for_updates():
        pass