import sqlite3
from datetime import datetime, date

def create_tables():
	table_product_information=""" CREATE TABLE IF NOT EXISTS product_information (
								product_title_id integer primary key autoincrement,
								product_title text NOT NULL UNIQUE,
								category text NOT NULL,
								brand text NOT NULL,
								model text NOT NULL UNIQUE )"""
	
	table_sites_items=""" CREATE TABLE IF NOT EXISTS sites_items (
						profiles_name text primary key,
						item_1_id text,
						item_2_id text,
						item_3_id text,
						item_4_id text,
						FOREIGN KEY(item_1_id) REFERENCES product_information(model)
						FOREIGN KEY(item_2_id) REFERENCES product_information(model)
						FOREIGN KEY(item_3_id) REFERENCES product_information(model)
						FOREIGN KEY(item_4_id) REFERENCES product_information(model))"""

	table_records= """CREATE TABLE IF NOT EXISTS records (
					record_id integer primary key autoincrement,
                    title text,
                    price float,
                    brand text,
                    date_of_scrap date,
                    url text,
                    deal boolean,
                    FOREIGN KEY(title) REFERENCES product_information(product_title))"""

if __name__ == '__main__':
	create_tables()
