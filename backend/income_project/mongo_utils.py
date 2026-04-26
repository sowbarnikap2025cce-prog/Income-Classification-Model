import os
from pymongo import MongoClient

def get_db():
    uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.environ.get('MONGO_DB_NAME', 'income_db')
    client = MongoClient(uri)
    return client[db_name]
