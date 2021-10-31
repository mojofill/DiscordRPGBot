import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

password = os.getenv('PASSWORD')

cluster = MongoClient(f'mongodb+srv://henryzhang:{password}@cluster0.xf1re.mongodb.net/myFirstDatabase?authSource=admin&replicaSet=atlas-b9ngb4-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true')

db = cluster.bot