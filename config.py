import os
from pymongo import MongoClient

# Environment Variables for MongoDB Connection
MONGO_URI = os.getenv("crawler_db_server", "mongodb://localhost:27017/")
DB_NAME = os.getenv("crawler_db_name", "crawler_db")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]