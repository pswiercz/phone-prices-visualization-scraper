import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
from tqdm import tqdm

def scrap(url):
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, features="html.parser")

    web_ids = {'title': ('productTitle', 'span'),
               'price': ('priceblock_ourprice', 'span'),
               'brand': ('bylineInfo', 'a')}

    try:
        str(soup).index(f'Robot Check')
        return 'Robot_Check'

    except:
        product_value = []
        try:
            for product_id, tag in web_ids.values():
                item_index = str(soup).index(f'id="{product_id}"')
                new_soup = str(soup)[item_index-10:]
                end_search = new_soup.index(f'</{tag}>')  
                new_soup = new_soup[:end_search+3+len(tag)]
                product_value.append(BeautifulSoup(new_soup, features="html.parser")
                                    .find(tag, {'id': product_id}).text.strip())
        
        except:
            return 'web_ids problem'
        else:
            from datetime import datetime
            product_value.extend((datetime.today().strftime('%Y-%m-%d'), url, False)) #3rd if promotion
            return product_value


import sqlite3
with sqlite3.connect(r'../website_end/database.db') as conn: #database.db
    def new_table_records():
        c = conn.cursor()
        c.execute("CREATE TABLE if NOT EXISTS records(record_id integer primary key autoincrement, \
                                                    title text, \
                                                    price float, \
                                                    site_brand text, \
                                                    date_of_scrap date, \
                                                    url text, \
                                                    deal boolean)")
        conn.commit()

    def add_to_db(item):
        item.insert(0, None)
        c = conn.cursor()
        c.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?)", tuple(item))
        conn.commit()

    def read_value():
        c = conn.cursor()
        c.execute("SELECT * FROM records")
        print(c.fetchall())

    def clear_db():
        c = conn.cursor()
        c.execute("DELETE FROM records")
        conn.commit()

    def drop_table():
        c = conn.cursor()
        c.execute("DROP TABLE records")
        conn.commit()

def main():
    # new_table_records()
    with open('urls.txt', 'r') as f:
        urls = list(set(f.readlines()))

    bad_urls = []
    for url in tqdm(urls):
        while True:
            try:
                result = scrap(url)
                if result != 'Robot_Check':
                    # if page is correct but there is problem with id (mostly price on site)
                    if result == 'web_ids problem':
                        bad_urls.append(url)
                    else:
                        add_to_db(result)
                    break
            except Exception as e:
                print(e)
    print(bad_urls)
    
if __name__ == '__main__':
    # drop_table()
    main()