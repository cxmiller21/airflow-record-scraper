from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
import json

inventory = []


@dataclass
class Record:
    artist: str
    title: str
    label: str
    year: str


@dataclass
class Inventory:
    records: list[Record]


inventory = Inventory(records=[])


def get_raw_page_data():
    artist = "119485-Tatsuro-Yamashita"
    url = f"https://www.discogs.com/artist/{artist}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


soup = get_raw_page_data()
table_rows = soup.find("table", class_="cards").findAll("tr", class_="card")

for row in table_rows:
    tds = row.findAll("td")
    inventory.records.append(
        Record(
            artist=tds[3].text, title=tds[4].a.text, label=tds[5].text, year=tds[8].text
        )
    )


print(len(inventory.records))
print(inventory.records)
