from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import Optional
import asyncio
from app.core.config import settings

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Create vector search index if it doesn't exist
        await create_vector_search_index()
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("🔌 Disconnected from MongoDB")

async def create_vector_search_index():
    """Check if vector search index exists (don't create it)"""
    try:
        collection = mongodb.database[settings.MONGODB_COLLECTION]
        
        # Check if index already exists
        existing_indexes = await collection.list_indexes().to_list(length=None)
        index_names = [idx['name'] for idx in existing_indexes]
        
        if settings.MONGODB_VECTOR_INDEX in index_names:
            print(f"✅ Vector search index found: {settings.MONGODB_VECTOR_INDEX}")
        else:
            print(f"ℹ️ Vector search index not found: {settings.MONGODB_VECTOR_INDEX}")
            print("ℹ️ Please create the vector search index manually in MongoDB Atlas")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not check vector search index: {e}")
        # Don't raise error as the app can still work without the index

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if mongodb.database is None:
        raise Exception("Database not connected. Call connect_to_mongo() first.")
    return mongodb.database

def get_collection():
    """Get course content collection"""
    database = get_database()
    return database[settings.MONGODB_COLLECTION]
