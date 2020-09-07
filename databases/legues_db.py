import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import functools
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text, bold, italic, code, pre

class LegueDB():
    """
    Include table in db for one legue
    """
    def __init__(self, legue_name, fonbet_url, repr_name=None):
        self.legue_name = legue_name
        self.repr_name = repr_name
        self.fonbet_url = fonbet_url
        self.teams = []
        self.coefs = []
        self.conn = sqlite3.connect("legues.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + legue_name + '''
                    (team_name text, team_vs_name text, coef_for real, coef_against real)
                ''')    

    def __str__(self):
        return emojize(self.__emojize_name() + " " + self.repr_name)

    def __emojize_name(self):
        emoji_dict = {
            "Russia" : "🇷🇺",
            "France" : "🇫🇷"
        }
        return emoji_dict[self.legue_name]

    def get_name(self):
        return self.legue_name
        
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
        driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
        driver.get(match_link)
        coef_1 = []
        coef_2 = []
        try:
            old_view = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'container--159-u'))
            )
            button = old_view.find_element_by_tag_name('a')
            button.click()
            for_coefs_1 = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'table__details'))
            )[8]
            for_coefs_2 = driver.find_elements_by_class_name('table__details')[9]
            against_coef = driver.find_elements_by_class_name('table__details')[0]
        except:
            # отправить сообщение об ошибке
            driver.quit()
        coef_1.append(float(for_coefs_1.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[1].text))
        coef_1.append(float(against_coef.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[2].text))
        coef_2.append(float(for_coefs_2.find_elements_by_class_name('table__grid-row')[2].find_elements_by_tag_name('td')[1].text))
        coef_2.append(float(against_coef.find_elements_by_class_name('table__grid-row')[1].find_elements_by_tag_name('td')[2].text))
        driver.quit()
        return [coef_1, coef_2]

    def update_coefs(self):
        """
        Update self.teams and self.coefs
        """
        driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
        driver.get(self.fonbet_url)
        try:
            table_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table'))
            ).find_elements_by_class_name('table__row')
        except:
            # отправить сообщение об ошибке
            driver.quit()
        self.coefs = [] # list of pairs of coefs
        self.teams = [] # list of teams' names
        for i in range(len(table_rows)-2):
            self.coefs += self.update_match_coefs(
                table_rows[i+1].find_element_by_class_name('table__match-title-text').get_attribute("href")
                )
            self.teams += self.update_match_name(
                table_rows[i+1].find_element_by_class_name('table__match-title-text').text
                )
        driver.quit()

    def update_db(self):
        """
        Rewrite teams and coefs in db
        """
        self.update_coefs()
        # clear table
        self.cursor.execute('DELETE FROM ' + self.legue_name)
        # colect insert data
        insert_data = []
        for i in range(0,len(self.teams),2):
            insert_data.append( (self.teams[i] + ' [д]', self.teams[i+1], self.coefs[i][0], self.coefs[i][1]) )
            insert_data.append( (self.teams[i+1] + ' [г]', self.teams[i], self.coefs[i+1][0], self.coefs[i+1][1]) )
        # insert data to db
        self.cursor.executemany('INSERT INTO ' + self.legue_name + ' VALUES (?,?,?,?)', insert_data)    
        self.conn.commit()
    
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
        team1_max_len = 9
        if len(db_tup[0])<=team1_max_len + 4:
            team1 = bold(db_tup[0] + "  ")
        else:
            team1 = bold(db_tup[0][:team1_max_len] + " " + db_tup[0].split()[-1] + "  ")
        team2_max_len = 9
        if len(db_tup[1])<=team2_max_len:
            team2 = italic("vs " + db_tup[1])
        else:
            team2 = italic("vs " + db_tup[1][:team2_max_len])
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