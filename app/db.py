import os
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ai_backend_db")  # fallback name if not set in .env

client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(MONGO_URI)
db: AsyncIOMotorDatabase[Any] = client[DB_NAME]
users_collection: AsyncIOMotorCollection[Any] = db["users"]