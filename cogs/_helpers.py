import discord
from datetime import datetime
from discord.ui import View, Button
import re
from urllib.parse import parse_qs
import urllib.parse as urlparse
import threading
import subprocess
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import *
from main import logger
import logging

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)



def embed(title,description,url=None):
    em = discord.Embed(title=title,description=description,color=discord.Color.green(),url="https://github.com/jsmsj/GcloneDiscordify",timestamp=datetime.now())
    em.set_footer(text="Made with 💖 by jsmsj.")
    if url:
        btn = Button(label="Link",url=url)
        view = View()
        view.add_item(btn)
        return [em,view]
    return [em,None]


class DriveUtil:
    def __init__(self,user_id) -> None:
        self.userid = user_id
        
        self.__OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']

        self.__service = self.authorize()

    def getIdFromUrl(self,link: str):
        regex = r"https://drive\.google\.com/(((drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/)|(open\?id=))([-\w]+)[?+]?/?(w+)?"
        res = re.search(regex,link)
        if res is None:
                raise IndexError("GDrive ID not found.")
        return res.group(8)
    
    def make_url(self,id):
        return f'https://drive.google.com/open?id={id}'
    

    @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
        retry=retry_if_exception_type(HttpError), before=before_log(logger, logging.DEBUG))
    def get_file_metadata(self,file_id):
        try:
            file = self.__service.files().get(supportsAllDrives=True, fileId=file_id, fields="name,size,mimeType").execute()
            return [file.get('name'),file.get('size'),file.get('mimeType')]
        except Exception:
            return [None,None,None]
        
    def authorize(self):
        with open('accounts/1.json') as f:
            sa_info = json.load(f)
        sa = {
            "client_email":sa_info["client_email"],
            "token_uri":sa_info["token_uri"],
            "private_key":sa_info["private_key"]
        }
        creds = service_account.Credentials.from_service_account_info(sa,scopes=self.__OAUTH_SCOPE)
        # http = httplib2.Http(timeout=5) see https://github.com/googleapis/google-api-python-client/issues/480
        # authed_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
        return build('drive', 'v3', credentials=creds, cache_discovery=False) #,http=authed_http
    
allthreads = {}

class SubprocThread(threading.Thread):
    def __init__(self,userid, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.daemon = True
        self.args = args
        self.critical_fault = False
        self.userid = userid
        self.output = ''


    def kill(self):
        self.critical_fault = True

    def run(self):
        source,dest = self.args
        thread_id = self.ident

        cmd = [
            'gclone',
            'copy',
            'GC:{{{}}}'.format(source),
            'GC:{{{}}}'.format(dest),
            '--drive-server-side-across-configs',
            '--progress',
            '--stats',
            '1s',
            '--ignore-existing',
            '--transfers',
            '8',
            '--tpslimit',
            '6'
        ]

        process = subprocess.Popen(cmd,
                                       bufsize=1,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       encoding='utf-8',
                                       errors='ignore',
                                       universal_newlines=True)
        
        

        while process.poll() is None:
            try:
                line = process.stdout.readline()
            except Exception as e:
                print(e)
                if process.poll() is not None:
                    break
                else:
                    continue
            if not line and process.poll() is not None:
                break

            output = line.rstrip()
            self.output = output

            if self.critical_fault:
                process.terminate()
                break
            


    

    

    
