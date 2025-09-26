"""
Quick setup script for MongoDB Atlas Vector Search
This script will test your connection and set up the vector search index
"""

import asyncio
import os
from app.database import connect_to_mongo, close_mongo_connection, get_collection
from app.core.config import settings

async def setup_mongodb():
    """Set up MongoDB with vector search index"""
    print("🚀 Setting up MongoDB Atlas Vector Search...")
    print(f"📡 Connecting to: {settings.MONGODB_URL[:50]}...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # Test database operations
        collection = get_collection()
        
        # Check if collection exists and get document count
        doc_count = await collection.count_documents({})
        print(f"📊 Database: {settings.MONGODB_DATABASE}")
        print(f"📁 Collection: {settings.MONGODB_COLLECTION}")
        print(f"📄 Documents: {doc_count}")
        
        # Create vector search index
        print("\n🔍 Setting up vector search index...")
        try:
            # Check if index already exists
            existing_indexes = await collection.list_indexes().to_list(length=None)
            index_names = [idx['name'] for idx in existing_indexes]
            
            if settings.MONGODB_VECTOR_INDEX not in index_names:
                print("⚠️ Vector search index not found. You need to create it manually in MongoDB Atlas.")
                print("\n📋 To create the vector search index:")
                print("1. Go to your MongoDB Atlas dashboard")
                print("2. Navigate to your cluster")
                print("3. Click 'Search' in the left sidebar")
                print("4. Click 'Create Search Index'")
                print("5. Choose 'JSON Editor'")
                print("6. Select your database and collection")
                print("7. Use this configuration:")
                print("""
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}""")
                print("8. Name your index 'vector_index'")
                print("9. Click 'Create Search Index'")
            else:
                print("✅ Vector search index already exists!")
        except Exception as e:
            print(f"⚠️ Could not check vector search index: {e}")
        
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Add your OpenAI API key to the environment")
        print("2. Run 'python seed_data.py' to add sample data")
        print("3. Start the API with 'python -m uvicorn app.main:app --reload'")
        print("4. Test the API at http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your MongoDB Atlas connection string")
        print("2. Ensure your IP address is whitelisted in MongoDB Atlas")
        print("3. Verify your database user has read/write permissions")
        print("4. Check your network connection")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("MongoDB Atlas Vector Search Setup")
    print("=" * 40)
    print(f"Database: {settings.MONGODB_DATABASE}")
    print(f"Collection: {settings.MONGODB_COLLECTION}")
    print("=" * 40)
    
    asyncio.run(setup_mongodb())
