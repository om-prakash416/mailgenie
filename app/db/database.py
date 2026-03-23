from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo():
    """
    Create MongoDB connection
    """
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB_NAME]

        # Ping database to verify connection
        await client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas")

    except ConnectionFailure as e:
        print("❌ MongoDB connection failed")
        raise e


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")


def get_database():
    """
    Get DB instance
    """
    return db
