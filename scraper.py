import datetime
import json
import os
import requests
import threading

from bs4 import BeautifulSoup as bs
from newspaper import Article

lock = threading.Semaphore(value=1)



def archive(date):

    url =  f'https://www.thehindu.com/archive/web/{date}'
    soup = bs(requests.get(url).text, 'html.parser')

    links = soup.find_all("ul", {"class": "archive-list"})
    heading = soup.find_all("a", {"class": "section-list-heading"})

    data = {}
    data['list'] = [(list((row.text, row['href']) 
        for row in element.find_all("a")), (head.text.split('\n')[1]) ) 
            for element, head in zip(links, heading)]

    with open(f'{date.replace("/", "_")}.json', 'w') as file:
        json.dump( data, file )


def article(url):
    
    lock.acquire()

    article3k = Article(url)
    article3k.download()
    article3k.parse()

    soup = bs(article3k.html, 'html.parser')
    
    try:
        section_name = soup.find("a", {"class": "section-name"}).text.split('\n')[1]
    except AttributeError:
        section_name = ' '
    title = soup.find("meta", {"name": "title"})['content']
    author = soup.find("meta", {"property": "article:author"})['content']

    publish_date_iso = soup.find("meta", {"name": "publish-date"})['content']
    publish_date_object = datetime.datetime.strptime(publish_date_iso, "%Y-%m-%dT%H:%M:%S%z")
    publish_date = datetime.datetime.strftime( publish_date_object, "%A %d, %Y %H:%M" )

    modified_date_iso = soup.find("meta", {"name": "modified-date"})['content']
    modified_date_object = datetime.datetime.strptime(modified_date_iso, "%Y-%m-%dT%H:%M:%S%z")
    modified_date = datetime.datetime.strftime( modified_date_object, "%A %d, %Y %H:%M" )

    description = soup.find("meta", {"name": "description"})['content']

    data = {}
    data['section_name'] = section_name
    data['title'] = title
    data['author'] = author
    data['publish_date'] = publish_date
    data['modified_date'] = modified_date
    data['description'] = description
    data['content'] = str(article3k.text)
    data['image'] = article3k.top_image

    with open(f'{url[-12:-4]}.json', 'w') as file:
        json.dump( data, file )

    lock.release()

