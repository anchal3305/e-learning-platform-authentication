import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client['User_Authentication']  # Replace with your database name