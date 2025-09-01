import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
DATABASE=os.getenv('DATABASE')
USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')

'''Data base configuration'''
conf = {
    'host':HOST,
    'port' : PORT,
    'database' : DATABASE,
    'user' : USER,
    'password' : PASSWORD
}


engine = create_engine("postgresql://{user}:{password}@{host}:{port}/{database}".format(**conf))