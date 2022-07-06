from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
import json

inventory = []

def get_raw_page_data():
    artist = "119485-Tatsuro-Yamashita"
    url = f"https://www.discogs.com/artist/{artist}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    return soup

soup = get_raw_page_data()
table_rows = soup.find("table", class_="cards").findAll('tr', class_='card')

for row in table_rows:
    data = {
        "artist": "",
        "title": "",
        "label": ""
    }
    
    for td in row.findAll('td'):
        td_class = td["class"]
        
        if "title" in td_class:
            data["title"] = td.a.text
        if "artist" in td_class:
            # print(td.a.text)
            data["artist"] = td.a.text
        if "label" in td_class:
            # print(td.a.text)
            data["label"] = td.a.text
    
    inventory.append(data)

print(inventory)