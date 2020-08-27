import sqlite3
from selenium import webdriver

class PlayersDB:
    def __init__(self, legue_name, legue_url, repr_name=None):
        self.legue_name = legue_name
        self.legue_url = legue_url
        self.repr_name = repr_name
        self.conn = sqlite3.connect("players.db")
        self.cursor = self.conn.cursor()
        # https://www.sports.ru/fantasy/football/tournament/49.html
        split_url = self.legue_url.split('/')
        # https://www.sports.ru/fantasy/football/tournament/ratings/popular/49.html
        self.popular_players_url = '/'.join(split_url[0:-1]) + '/ratings/popular/' + split_url[-1]

    def get_name(self):
        return self.legue_name

    def __str__(self):
        return self.__emojize_name() + " " + self.repr_name

    def __emojize_name(self):
        emoji_dict = {
            "Russia" : "🇷🇺",
            "France" : "🇫🇷"
        }
        return emoji_dict[self.legue_name]

    def get_popular(self):
        """
        Return message to user
        """
        self.cursor.execute('SELECT * FROM ' + self.legue_name + """
            ORDER BY dif_popularity
            LIMIT 10
        """)
        best_players = self.cursor.fetchall()
        self.cursor.execute('SELECT * FROM ' + self.legue_name + """
            ORDER BY dif_popularity
            LIMIT 10
        """)
        whorst_players = self.cursor.fetchall()
        return self.__get_message(best_players, whorst_players)

    def __get_message(self, best_players, whorst_players):
        return best_players + whorst_players

    def create_db(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.legue_name + '''
                    (first_name text, team text, amplua integer, 
                    new_popularity integer, dif_popularity integer)
                ''')
        self.create_page(self.popular_players_url)
        j = 2
        while self.create_page(self.popular_players_url + '?p=' + str(j)):
            j = j + 1

    def update_db(self):
        self.update_page(self.popular_players_url)
        j = 2
        while self.update_page(self.popular_players_url + '?p=' + str(j)):
            j = j + 1

    def create_page(self, url):
        driver = webdriver.Firefox()
        driver.get(url)
        players_on_page = driver.find_elements_by_tag_name('tr')
        count_of_players_on_page = len(players_on_page)
        if count_of_players_on_page < 2:
            driver.close()
            return False
        for i in range(count_of_players_on_page-1):
            player_name = players_on_page[i+1].find_element_by_class_name('name').text
            player_amplua = players_on_page[i+1].find_element_by_class_name('overBox').text.split('\n')[1]
            player_population = int(players_on_page[i+1].find_elements_by_tag_name('td')[1].text)
            player_team = players_on_page[i+1].find_elements_by_tag_name('a')[1].text
            self.__add_player(player_name, player_amplua, player_population, player_team)
        driver.close()
        return True

    def __add_player(self, player_name, player_amplua, player_population, player_team):
        self.cursor.execute("INSERT INTO " + self.legue_name + " VALUES (?,?,?,?,?)", 
            (player_name, player_team, player_amplua, player_population, 0)
        )
        self.conn.commit()

    def update_page(self, url):
        driver = webdriver.Firefox()
        driver.get(url)
        players_on_page = driver.find_elements_by_tag_name('tr')
        count_of_players_on_page = len(players_on_page)
        if count_of_players_on_page < 2:
            driver.close()
            raise Exception()
        for i in range(count_of_players_on_page-1):
            player_name = players_on_page[i+1].find_element_by_class_name('name').text
            new_population = int(players_on_page[i+1].find_elements_by_tag_name('td')[1].text)
            # update row in db
            if not self.__update_player(player_name, new_population):
                player_amplua = players_on_page[i+1].find_element_by_class_name('overBox').text.split('\n')[1]
                player_team = players_on_page[i+1].find_elements_by_tag_name('a')[1].text
                self.__add_player(player_name, player_amplua, new_population, player_team)
        driver.close()

    def __update_player(self, player_name, new_population):
        self.cursor.execute("SELECT * FROM " + self.legue_name + """
            WHERE first_name = ?
        """, (player_name, )) 
        player_data = self.cursor.fetchone()
        if player_data==[]:
            return False
        else:
            self.cursor.execute("UPDATE " + self.legue_name + """
                SET dif_popularity = ? ,
                    new_popularity = ?
                WHERE first_name = ?
            """, 
            (new_population - player_data[4], new_population, player_name))
        self.conn.commit()
        return True

if __name__=='__main__':
    Spain = PlayersDB('Spain', 'https://www.sports.ru/fantasy/football/tournament/49.html', 'ЛаЛига')
    Spain.update_db()