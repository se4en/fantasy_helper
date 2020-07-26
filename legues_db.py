import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LegueDB():
    def __init__(self, legue_name, fonbet_url):
        self.legue_name = legue_name
        self.fonbet_url = fonbet_url
        self.conn = sqlite3.connect("legues.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ' + legue_name + '''
                    (team_name text, team_vs_name text, coef_for real, coef_against real)
                ''')
            
    def update_match(self, match_name, match_link):
        teams = match_name.split(' ').remove('-')
        driver = webdriver.Firefox()
        driver.get(match_link)
        #
        return teams, coefs


    def update_coefs(self):
        driver = webdriver.Firefox()
        driver.get(self.fonbet_url)
        try:
            table_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table'))
            ).find_elements_by_class_name('table__row')

        finally:
            # отправить сообщение об ошибке
            driver.quit()
        #table_rows = driver.find_element_by_class_name('table').find_elements_by_class_name('table-row')
        teams = []
        coefs = []
        for i in range(len(table_rows)):
            table_rows[i].find_element_by_class_name('table__match-title-text').get_attribute('href')
            print(i)
            #zip(teams, coefs) = update_coefs(table)
        #matches = list(map(find_element_by_class_name('table__match-title-text'), table_rows))
        driver.quit()


    def get_coefs(self):
        return 1

if __name__=='__main__':
    Italy = LegueDB('Италия', 'https://www.fonbet.ru/bets/football/11924/')
    Italy.update_coefs()
    coefs = Italy.get_coefs()
    print(coefs)