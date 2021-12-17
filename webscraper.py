from bs4 import BeautifulSoup
import requests, time
import json

data_dict = {'name':[], 'date':[], 'platform': [], 'score':[], 'url':[], 'userscore':[], 'genre':[]} # Data Structure

url = "https://www.metacritic.com/browse/games/release-date/available/switch/metascore?page=0"
userAgent = {'User-agent': 'Mozilla/5.0'}
source = requests.get(url, headers=userAgent).text
soup = BeautifulSoup(source, 'html.parser')  
content = soup.find_all('table')
tblnum = 0
while tblnum < len(content):
    table_rows = content[tblnum].find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        if td!=[]:
            for a in td[1].find_all('a', {"class":"title"}):
                data_dict['name'].append(a.find('h3').text)
            for date in td[1].find_all('span',{"class":""}):
                data_dict['date'].append(date.text)
            for platform in td[1].find_all('span',{"class":"data"}):
                data_dict['platform'].append(platform.text.strip())
            scores =  td[1].find_all('div',{"class":"metascore_w"})
            data_dict['score'].append(scores[0].text.strip())
            data_dict['userscore'].append(scores[2].text.strip())
            for a in td[1].find_all('a', {"class":"title"} ,href=True):
                data_dict['url'].append(a['href'])
    tblnum += 1

baseUrl = "https://www.metacritic.com"
for url in data_dict['url']:
    fullUrl = baseUrl + url
    source = requests.get(fullUrl, headers=userAgent).text
    soup = BeautifulSoup(source, 'html.parser')  
    content = soup.find_all('li', {"class" : "summary_detail product_genre"})
    genre_str = ""
    for item in content:  
        genres = item.find_all('span', {"class" : "data"})
        for genre in genres:
            if genre == genres[-1]:
                genre_str += genre.text.strip() 
            else:
                genre_str += genre.text.strip() + ","
    data_dict['genre'].append(genre_str)
    time.sleep(5)

#print(data_dict)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=4)

