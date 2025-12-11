import os
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client["ai_receptionist"]
agents_collection = db["agents"]

# List all agents
for agent in agents_collection.find():
    print(agent)
