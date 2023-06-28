import json, time, requests
from bs4 import BeautifulSoup
from config import HEADERS

URL = "https://maroc.welipro.com/"

html = requests.get(URL, headers=HEADERS).text

parser = BeautifulSoup(html, 'html.parser')

cities_list = parser.find_all("option")
cities = {}
i = 1

while i<len(cities_list):
    city = {cities_list[i].text : cities_list[i].get("value")}
    print(city)
    cities.update(city)
    i += 1

with open("cities.json", 'w') as f:
    f.write(json.dumps(cities))