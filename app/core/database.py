from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_db():
    return db.client[os.getenv("DB_NAME", "dailyverse_db")]

async def connect_db():
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))

async def close_db():
    db.client.close()