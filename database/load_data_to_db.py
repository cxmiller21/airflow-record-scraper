import csv

import MySQLdb
import MySQLdb.cursors


FILE_NAME = "../exports/119485-Tatsuro-Yamashita_records_for_sale.csv"


def get_record_data_from_csv(file_name: str) -> list[dict]:
    """Get the record data from the csv file"""
    with open(file_name, "r") as file:
        reader = csv.DictReader(file)
        return list(reader)


def clean_record_data(record_data: list[dict]) -> list[dict]:
    """Clean the record data"""
    for data in record_data:
        if not data["seller_rating"]:
            data[""] = 0
    return record_data


def write_data_to_mysql(records: list[set]) -> None:
    """Write the data to the mysql database"""
    db = MySQLdb.connect(
        host="127.0.0.1",
        user="root",
        passwd="root",
        db="vinyl_records",
        port=3306,
        cursorclass=MySQLdb.cursors.DictCursor,
    )
    cursor = db.cursor()
    try:
        cursor.executemany(
            """INSERT IGNORE INTO vinyl (title, media_condition,
                        sleeve_condition, price, buy_url, seller_rating, seller_url)
                        VALUES (%(title)s, %(media_condition)s, %(sleeve_condition)s,
                        %(price)s, %(buy_url)s, %(seller_rating)s, %(seller_url)s)""",
            records,
        )
        db.commit()
    except Exception as e:
        raise e
    finally:
        db.close()


def main():
    record_data = get_record_data_from_csv(FILE_NAME)
    clean_data = clean_record_data(record_data)
    write_data_to_mysql(clean_data)
    print(f"Completed uploading {len(clean_data)} records to the database")


if __name__ == "__main__":
    main()
