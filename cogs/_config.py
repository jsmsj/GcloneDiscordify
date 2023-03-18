from dotenv import load_dotenv
import os
load_dotenv()

bot_token = os.getenv('bot_token')
prefix:str = os.getenv('prefix','g ')
default_destination_id = os.getenv('default_destination_id',None)