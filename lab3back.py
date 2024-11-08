import urllib.request as ur
import requests
from bs4 import BeautifulSoup 
from urllib.parse import urljoin
import json
import sqlite3
# Alyssa Goldgeisser
# Lab 3
# Module 3
# lab3back

#'''

base_url = 'https://www.timeout.com/things-to-do/best-places-to-travel'
page = requests.get(base_url)
soup = BeautifulSoup(page.content, "lxml")
soup.text.encode("utf8", "ignore").decode()

base_tag = base_url[:23]
data_list = []


for tag in soup.find_all('a', class_='_titleLinkContainer_142mc_45'):
    month_name = tag.text
    url = tag.get('href')
    link = urljoin(base_tag, url)
    link_page = requests.get(link)
    link_soup = BeautifulSoup(link_page.content, "lxml")
       
    for line, summary_tag in zip(link_soup.find_all('h3'), link_soup.find_all('div', class_='_summary_kc5qn_21')):
        try:
            rank, destination_tag = line.text.split('.', 1)
            rank = rank.strip()
            destination_tag = destination_tag.strip()
            finished_text = summary_tag.text.strip().split('.\n')
        
            a_tag = line.find_parent('a', target='_blank', rel='noopener noreferer')
            
            if a_tag:
                country_url = a_tag.get('href')
                if country_url.startswith("https"):
                    pass
                else:
                    country_url = urljoin(base_tag, country_url)   
            else:
                country_url = 'no url'

            data_list.append({
                'month': month_name,
                'rank': rank,
                'destination': destination_tag,
                'finished_text': finished_text[0],
                'destination_link' : country_url
            })
        except ValueError:
            pass

with open('travel_data.json', 'w') as f:
    json.dump(data_list, f, indent=4)

#'''

with open('travel_data.json', 'r') as f:
    data_list = json.load(f)

conn = sqlite3.connect('travel_data.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS months (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month_name TEXT UNIQUE
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month_id INTEGER,
    rank INTEGER,
    destination TEXT,
    finished_text TEXT,
    destination_link TEXT,
    FOREIGN KEY (month_id) REFERENCES months (id)
)
''')

def get_or_create_month(month_name):
    cur.execute('SELECT id FROM months WHERE month_name = ?', (month_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        cur.execute('INSERT INTO months (month_name) VALUES (?)', (month_name,))
        conn.commit()
        return cur.lastrowid

for item in data_list:
    try:
        month_name = item['month']
        month_id = get_or_create_month(month_name)
        rank = int(item['rank']) if item['rank'].isdigit() else None
        destination = item['destination name']
        finished_text = item['text']
        destination_link = item.get('url', None)  # Use .get to provide a default value

        cur.execute('''
        INSERT INTO destinations (month_id, rank, destination, finished_text, destination_link)
        VALUES (?, ?, ?, ?, ?)
        ''', (month_id, rank, destination, finished_text, destination_link))

    except KeyError as e:
        print(f"Missing key: {e} in item: {item}")

conn.commit()
conn.close()
