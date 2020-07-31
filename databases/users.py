from selenium import webdriver
from multiprocessing import Process

def get_teams(profile_url):
    driver = webdriver.Firefox()
    driver.get(profile_url + 'fantasy/')
    teams = driver.find_elements_by_class_name('league')
    result = {}
    for i in range(len(teams)):
        team = teams[i].find_elements_by_tag_name('a')
        team_url = team[0].get_attribute('href')
        team_name = team[1].text
        result[team_name] = team_url
    driver.quit()
    return result

def get_player_name(team_url, player_id):
    driver = webdriver.Firefox()
    driver.get(team_url + '#' + player_id)
    result = driver.find_elements_by_class_name('big-title')[1].find_element_by_class_name('titleH1').text
    driver.quit()
    return result

def get_team(team_url):
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
        proc = Process(target=get_player_name, args=(team_url, players_id[i],))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    return result

if __name__=='__main__':
    team_dict = get_teams('https://www.sports.ru/profile/142098017/')
    print(team_dict)
    team = get_team('https://www.sports.ru/fantasy/football/team/points/2156172.html')
    print(team)