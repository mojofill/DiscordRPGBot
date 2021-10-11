import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

password = os.getenv('PASSWORD')

cluster = MongoClient(f'mongodb+srv://henryzhang:{password}@cluster0.xf1re.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = cluster.bot