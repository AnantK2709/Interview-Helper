from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None

db = MongoDB()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient("mongodb://localhost:27017")
    db.db = db.client.interview_app
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")