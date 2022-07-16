import json
import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass


ARTIST = "119485-Tatsuro-Yamashita"
BASE_URL = "https://www.discogs.com"
ARTIST_URL = f"{BASE_URL}/artist/{ARTIST}"


@dataclass
class Record:
    title: str
    media_condition: str
    sleeve_condition: str
    price: str
    buy_url: str
    seller_url: str
    seller_rating: str


@dataclass
class Album:
    discogs_master_id: str
    artist: str
    title: str
    label: str
    year: str
    link: str
    records: list[Record]

    def add_record(self, record: Record) -> None:
        self.records.append(record)


@dataclass
class Inventory:
    albums: list[Album]

    def add_album(self, album: Album) -> None:
        self.albums.append(album)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def get_bs4_data(url: str) -> BeautifulSoup:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


inventory = Inventory(albums=[])
raw_artist_data = get_bs4_data(ARTIST_URL)
table_rows = raw_artist_data.find("table", class_="cards").findAll("tr", class_="card")

for row in table_rows:
    tds = row.findAll("td")
    link = tds[4].a["href"]

    if not link.startswith("/master/"):
        continue

    # href format is /master/unique_number_id-Album-Title
    master_id = link.replace("/master/", "").split("-")[0]
    inventory.add_album(
        Album(
            discogs_master_id=master_id,
            artist=tds[3].text,
            title=tds[4].a.text,
            label=tds[5].text,
            year=tds[8].text,
            link=link,
            records=[],
        )
    )


print(f"Found {len(inventory.albums)} albums")

for album in inventory.albums:
    vinyl_link = f"{BASE_URL}/sell/list?master_id={album.discogs_master_id}&ev=mb&format=Vinyl&currency=USD"
    raw_vinyl_data = get_bs4_data(vinyl_link)

    if raw_vinyl_data.find("table") is None:
        continue

    vinyl_rows = raw_vinyl_data.find("table", class_="mpitems").findAll(
        "tr", class_="shortcut_navigable"
    )

    for row in vinyl_rows:
        tds = row.findAll("td")

        if len(tds) < 2:
            continue

        record = Record(
            title=tds[1].a.text,
            media_condition="not sure how to get this...",
            sleeve_condition=tds[1].find("span", class_="item_sleeve_condition").text,
            price="",
            buy_url=tds[1].a["href"],
            seller_rating="",
            seller_url="",
        )

        if tds[4].find("span", class_="converted_price") is not None:
            record.price = tds[4].find("span", class_="converted_price").text.strip()

        seller_info = tds[2].findAll("strong")
        for x in seller_info:
            if x.find("a") is not None:
                record.seller_url = x.find("a")["href"]
            if "%" in x.text:
                record.seller_rating = x.text

        album.add_record(record)



with open("vinyl_records.json", "w") as f:
    f.write(inventory.toJSON())
