import sqlite3
from selenium import webdriver

class Exception(BaseException):
    def __init__(self):
        pass

class PlayersDB:
    def __init__(self, legue_name, legue_url, fonbet_url):
        self.legue_name = legue_name
        self.legue_url = legue_url
        self.fonbet_url = fonbet_url
        self.conn = sqlite3.connect("players.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + legue_name + '''
                    (first_name text, second_name text, team text, 
                    amplua integer, price real, old_popularity integer, 
                    new_popularity integer, rating integer)
                ''')

    '''   
    def update_coefs(self):
        driver = webdriver.Firefox()
        driver.get(self.fonbet_url)
    '''
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
            player_amplua = players_on_page[i+1].find_element_by_class_name('overBox').text.split('\n')[1]
            player_population = int(players_on_page[i+1].find_elements_by_tag_name('td')[1].text)
            player_team = players_on_page[i+1].find_elements_by_tag_name('a')[1].text

            print(player_name, player_team, player_population, player_amplua)
        driver.close()

    def update(self):
        # https://www.sports.ru/fantasy/football/tournament/49.html
        split_url = self.legue_url.split('/')
        # https://www.sports.ru/fantasy/football/tournament/ratings/popular/49.html
        self.popular_players_url = '/'.join(split_url[0:-1]) + '/ratings/popular/' + split_url[-1]
        self.update_page(self.popular_players_url)
        try:
            j = 2
            while True:
                self.update_page(self.popular_players_url + '?p=' + str(j))
                j = j + 1
        except(Exception): 
            pass

    def update_players_popularity(self):
        pass
    def update_players_rating(self):
        pass
    
if __name__=='__main__':
    Spain = PlayersDB('испания', 'https://www.sports.ru/fantasy/football/tournament/49.html', 'https://www.fonbet.ru/bets/football/11922/')
    Spain.update()