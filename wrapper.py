import json
import logging
import multiprocessing
import os
import queue
import requests
import shutil
import sys
import threading
import time
import uuid

from pydrive_util import upload_file, download_file
from pymongo import MongoClient
from scraper import archive, article
from time import process_time, sleep

__author__ = "jayvasantjv"


q = queue.Queue()
logging.basicConfig( level=logging.DEBUG, filename='wrapper.log', format='%(message)s')
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

client = MongoClient(os.getenv('DB_KEY'))
dbmain = client['drive_wrapper']
db = dbmain['users']


ids = queue.Queue()
def wrapper_util(link):
    q.get()
    try:
        article(link)
        print('downloaded! ',link[-12:-4] )
        id = upload_file(f'{link[-12:-4]}', 'json')
        print( 'file uploaded! ', id )
    except:
        id = 404
    ids.put(id)
    q.task_done()


def wrapper(date):
    archive(date)
    data = json.load(open(f'{date.replace("/", "_")}.json'))
    print(upload_file(str(date.replace("/", "_")), 'json'))
    
    jdata = data
    links = data['list']
    for link in links:
        link[1] = str(link[1])
        for li in link[0]:
            li[0] = str(li[0])
            q.put(li[1])
            wrapper_util(li[1])
            # threading.Thread(target=wrapper_util, args=(li[1],)).start()
    q.join()
    data = {}
    links = []
    for link in jdata['list']:
        file_ids = []
        section = {}
        for li in link[0]:
            file_id = {}
            file_id['title'] = li[0] 
            file_id['id'] = ids.get(0)
            file_ids.append( file_id )
        section['head'] = link[1] 
        section['link'] = file_ids
        links.append(section)
    data['list'] = links
    
    with open(f'{date.replace("/", "_")}.json', 'w') as file:
        json.dump( data, file )
    print(upload_file(f'{date.replace("/", "_")}','json'), ' this!!!! ')
