import threading
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()

gauth.LoadCredentialsFile("cred.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("cred.txt")

os.chdir('static')
drive = GoogleDrive(gauth)
http = drive.auth.Get_Http_Object()

lock = threading.Semaphore(value=1)


def create_folder():
    file = drive.CreateFile({'title': 'DriveWrapper', 
        "mimeType": "application/vnd.google-apps.folder"})
    file.Upload(param={'http':http})
    file.InsertPermission({ 
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader' })
    folder_id = file['id']
    return file['id']


def upload_file( filetitle, format ):
    lock.acquire()
    file = drive.CreateFile({ 'parents': [{'id': os.getenv('FOLDER_ID')}] })
    file.SetContentFile(f'{filetitle}.{format}')
    file.Upload(param={'http':http})
    lock.release()
    return file['id']


def download_file(id):
    file = drive.CreateFile({'id':id})
    file.GetContentFile(file['title'])
    return file['title']


def delete_file( id ):
    file = drive.CreateFile({'id': id})
    file.Delete()
    

def list_file( parents ):
    file_list = drive.ListFile({'q': f"'{parents}' in parents"}).GetList()

    for file1 in file_list:
        print( 'title: {}, id: {}'.format(file1['title'], file1['id'])  )