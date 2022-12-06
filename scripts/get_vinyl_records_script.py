import requests
import csv

from bs4 import BeautifulSoup
from dataclasses import dataclass


LIMIT = "10"

ARTIST = "119485-Tatsuro-Yamashita"
BASE_URL = "https://www.discogs.com"
ARTIST_URL = f"{BASE_URL}/artist/{ARTIST}"
ALBUM_URL = f"{ARTIST_URL}?limit={LIMIT}&type=Releases&subtype=Albums&filter_anv=0"

EXPORT_FILE_NAME = f"../exports/{ARTIST}_records_for_sale.csv"


@dataclass
class Album:
    discogs_master_id: str
    title: str
    label: str
    year: str
    link: str


@dataclass
class Artist:
    albums: list[Album]

    def add_album(self, album: Album) -> None:
        self.albums.append(album)


def get_bs4_data(url: str) -> BeautifulSoup:
    """Get beautiful soup data based on url"""
    headers = {"User-Agent":"Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def get_master_id(url: str) -> str:
    """Returns the master id from the link"""
    return url.replace("/master/", "").split("-")[0]


def get_record_price(price: str) -> float:
    """Get the float price from the record"""
    clean_price = price.replace(",", "").replace("$", "").replace(" total", "")
    return float(clean_price)


def get_albums_for_artist(url: str) -> Artist:
    """Returns a list of albums for the artist"""
    artist = Artist(albums=[])
    raw_artist_data = get_bs4_data(url)
    # print(raw_artist_data)
    table_rows = raw_artist_data.find("table", class_="cards").findAll(
        "tr", class_="card"
    )

    for row in table_rows:
        tds = row.findAll("td")
        link = tds[4].a["href"]

        if not link.startswith("/master/"):
            continue

        artist.add_album(
            Album(
                discogs_master_id=get_master_id(link),
                title=tds[4].a.text,
                label=tds[5].text,
                year=tds[8].text,
                link=link,
            )
        )
    return artist


def get_records_for_sale(album: Album) -> Album | None:
    """Get records for sale"""
    records = []

    record_link = f"{BASE_URL}/sell/list?master_id={album.discogs_master_id}&ev=mb&format=Vinyl&currency=USD"
    raw_data = get_bs4_data(record_link)

    if raw_data.find("table") is None:
        return None

    rows = raw_data.find("table", class_="mpitems").findAll(
        "tr", class_="shortcut_navigable"
    )

    for row in rows:
        tds = row.findAll("td")

        if len(tds) < 2:
            continue

        sleeve_condition = ""
        if tds[1].find("span", class_="item_sleeve_condition") is not None:
            sleeve_condition = tds[1].find("span", class_="item_sleeve_condition").text
        
        item_condition = "" 
        if tds[1].find("span", class_="has-tooltip") is not None:
            item_condition = (
                tds[1].find("span", class_="has-tooltip").previous_sibling.text.strip()
            )
        title = tds[1].find("a", class_="item_description_title").text

        record = {
            "title": title,
            "media_condition": item_condition,
            "sleeve_condition": sleeve_condition,
            "price": "",
            "buy_url": f"{BASE_URL}{tds[1].a['href']}",
            "seller_rating": "",
            "seller_url": "",
        }

        if tds[4].find("span", class_="converted_price") is not None:
            raw_price = tds[4].find("span", class_="converted_price").text.strip()
            record["price"] = get_record_price(raw_price)

        seller_info = tds[2].findAll("strong")

        for x in seller_info:
            if x.find("a") is not None:
                record["seller_url"] = f"{BASE_URL}{x.find('a')['href']}"
            if "%" in x.text:
                record["seller_rating"] = float(x.text.replace("%", ""))

        records.append(record)

    return records


def main():
    records_for_sale = []
    artist = get_albums_for_artist(ARTIST_URL)

    for album in artist.albums:
        records = get_records_for_sale(album)

        if records is None:
            continue

        records_for_sale = records_for_sale + records

    with open(EXPORT_FILE_NAME, "w") as f:
        csv_keys = records_for_sale[0].keys()
        writer = csv.DictWriter(f, csv_keys)
        writer.writeheader()
        writer.writerows(records_for_sale)



if __name__ == "__main__":
    main()
