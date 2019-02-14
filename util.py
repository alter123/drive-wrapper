import time
import json 
from pydrive_util import download_file

def download_data(file_id):
    return json.load(open(download_file( file_id )))
