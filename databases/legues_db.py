import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram.utils.markdown import text
from aiogram.utils.emoji import emojize

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
        return emojize(":ru: " + self.repr_name)

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
        driver = webdriver.Firefox()
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
        driver = webdriver.Firefox()
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
            insert_data.append( (self.teams[i], self.teams[i+1], self.coefs[i][0], self.coefs[i][1]) )
            insert_data.append( (self.teams[i+1], self.teams[i], self.coefs[i+1][0], self.coefs[i+1][1]) )
        # insert data to db
        self.cursor.executemany('INSERT INTO ' + self.legue_name + ' VALUES (?,?,?,?)', insert_data)    
    
    def get_coefs(self):
        """
        Return list of tuple of row from db for each team
        """
        self.cursor.execute('SELECT * FROM ' + self.legue_name)
        return self.cursor.fetchall()

if __name__=='__main__':
    Italy = LegueDB('Италия', 'https://www.fonbet.ru/bets/football/11924/')
    Italy.update_db()
    coefs = Italy.get_coefs()
    print(coefs)