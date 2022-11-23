"""
### ETL DAG Tutorial Documentation
This ETL DAG is demonstrating an Extract -> Transform -> Load pipeline
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from textwrap import dedent
from bs4 import BeautifulSoup

import boto3
import csv
import json
import pendulum
import requests


LIMIT = "500"

ARTIST = "119485-Tatsuro-Yamashita"
BASE_URL = "https://www.discogs.com"
ARTIST_URL = f"{BASE_URL}/artist/{ARTIST}"
ALBUM_URL = f"{ARTIST_URL}?limit={LIMIT}&type=Releases&subtype=Albums&filter_anv=0"

EXPORT_FILE_NAME = f"./exports/{ARTIST}_records_for_sale.csv"
S3_BUCKET = "airflow-training-data"
S3_KEY = f"export/record-data.csv"


def get_bs4_data(url: str) -> BeautifulSoup:
    """Get beautiful soup data based on url"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def get_master_id(url: str) -> str:
    """Returns the master id from the link"""
    return url.replace("/master/", "").split("-")[0]


def get_record_price(price: str) -> float:
    """Get the float price from the record"""
    clean_price = price.replace(",", "").replace("$", "").replace(" total", "")
    return float(clean_price)


def get_albums_for_artist(url: str) -> list:
    """Returns a list of albums for the artist"""
    albums = []
    raw_artist_data = get_bs4_data(url)
    table_rows = raw_artist_data.find("table", class_="cards").findAll(
        "tr", class_="card"
    )

    for row in table_rows:
        tds = row.findAll("td")
        link = tds[4].a["href"]

        if not link.startswith("/master/"):
            continue

        album = {
            "discogs_master_id": get_master_id(link),
            "title": tds[4].a.text,
            "label": tds[5].text,
            "year": tds[8].text,
            "link": link,
        }

        albums.append(album)
    return albums


def get_records_for_sale(album: dict) -> dict:
    """Get records for sale"""
    records = []

    record_link = f"{BASE_URL}/sell/list?master_id={album['discogs_master_id']}&ev=mb&format=Vinyl&currency=USD"
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


with DAG(
    "vinly_record_etl_dag",
    # [START default_args]
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={"retries": 2},
    description="ETL DAG for Vinyl Records",
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["test"],
) as dag:
    dag.doc_md = __doc__

    def extract(**kwargs):
        ti = kwargs["ti"]
        records_for_sale = []
        albums = get_albums_for_artist(ARTIST_URL)

        for album in albums:
            records = get_records_for_sale(album)

            if records is None:
                continue

            records_for_sale = records_for_sale + records

        ti.xcom_push("record_data", records_for_sale)

    def transform(**kwargs):
        ti = kwargs["ti"]
        extract_data = ti.xcom_pull(task_ids="extract", key="record_data")
        print(extract_data)
        total_record_value = len(extract_data)

        total_value = {"total_record_value": total_record_value}
        total_value_json_string = json.dumps(total_value)
        ti.xcom_push("extract_data", extract_data)

    def load(**kwargs):
        ti = kwargs["ti"]
        total_value_string = ti.xcom_pull(
            task_ids="transform", key="extract_data"
        )
        extract_data = json.loads(total_value_string)
        print(extract_data)

        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_KEY,
            Body=json.dumps(extract_data)
        )

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )
    extract_task.doc_md = dedent(
        """\
    #### Extract task
    A simple Extract task to get data ready for the rest of the data pipeline.
    In this case, getting data is simulated by reading from a hardcoded JSON string.
    This data is then put into xcom, so that it can be processed by the next task.
    """
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )
    transform_task.doc_md = dedent(
        """\
    #### Transform task
    A simple Transform task which takes in the collection of order data from xcom
    and computes the total order value.
    This computed value is then put into xcom, so that it can be processed by the next task.
    """
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )
    load_task.doc_md = dedent(
        """\
    #### Load task
    A simple Load task which takes in the result of the Transform task, by reading it
    from xcom and instead of saving it to end user review, just prints it out.
    """
    )

    extract_task >> transform_task >> load_task
