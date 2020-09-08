import sqlite3
from selenium import webdriver
from multiprocessing import Process

class UsersDB:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread = False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                            (tg_id int, profile_url text)
                            """)

    def add_user(self, tg_id, profile_url=None):
        self.cursor.execute('INSERT INTO users VALUES (?, ?)', (tg_id, profile_url))
        self.conn.commit()
    
    def add_profile(self, tg_id, profile_url):
        # поменять!
        self.cursor.execute('INSERT INTO users VALUES (?, ?)', (tg_id, profile_url))
        self.conn.commit()

    def check_password(self, tg_id):
        self.cursor.execute('SELECT * FROM users WHERE tg_id=?', [(tg_id)])
        result = self.cursor.fetchone()
        return True if result else False

    def get_profile(self, tg_id):
        self.cursor.execute('SELECT * FROM users WHERE tg_id=?', [(tg_id)])
        result = self.cursor.fetchone()
        return result[1] if result else None

    def get_teams(self, tg_id):
        driver = webdriver.Firefox()
        driver.get(self.get_profile(tg_id) + 'fantasy/')
        teams = driver.find_elements_by_class_name('league')
        result = {}
        for i in range(len(teams)):
            team = teams[i].find_elements_by_tag_name('a')
            team_url = team[0].get_attribute('href')
            team_name = team[1].text
            result[team_name] = team_url
        driver.quit()
        return result
 
    def get_player_name(self, team_url, player_id):
        driver = webdriver.Firefox()
        driver.get(team_url + '#' + player_id)
        result = driver.find_elements_by_class_name('big-title')[1].find_element_by_class_name('titleH1').text
        driver.quit()
        return result

    def get_team(self, team_url):
        driver = webdriver.Firefox()
        driver.get(team_url)
        players = driver.find_element_by_class_name('forward-container').find_elements_by_tag_name('ins')
        players += driver.find_element_by_class_name('halfback-container').find_elements_by_tag_name('ins')
        players += driver.find_element_by_class_name('defender-container').find_elements_by_tag_name('ins')
        players += driver.find_element_by_class_name('goalkeeper-container').find_elements_by_tag_name('ins')
        players += driver.find_element_by_class_name('reserve-container').find_elements_by_tag_name('ins')
        players_id = []
        for i in range(len(players)):
            players_id.append(players[i].get_attribute('data-id'))
        result = [] 
        driver.quit()
        procs = [] 
        for i in range(len(players)):
            proc = Process(target=self.get_player_name, args=(team_url, players_id[i],))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
        return result