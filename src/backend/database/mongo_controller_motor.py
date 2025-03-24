

# TODO: AI Generated Controller. Will be switching to this before next milestone. Template here for now.

# import os
# from typing import Dict, List, Any, Optional
# from bson import ObjectId
# from datetime import datetime
# from dotenv import load_dotenv

# import motor.motor_asyncio

# load_dotenv()

# class AsyncMongoDBController:
#     """Asynchronous MongoDB controller using Motor for MongoDB Atlas"""

#     def __init__(self):
#         # Get the URI from the environment variables
#         self.uri = os.getenv("MONGO_DB_URI")
#         self.client = None
        
#     async def connect(self) -> None:
#         """Connect to MongoDB Atlas"""
#         if not self.client:
#             self.client = motor.motor_asyncio.AsyncIOMotorClient(self.uri)
#         return self.client
    
#     async def close(self) -> None:
#         """Close the MongoDB connection"""
#         if self.client:
#             self.client.close()
#             self.client = None
    
#     async def get_database(self, db_name: str):
#         """Get a database by name"""
#         client = await self.connect()
#         return client[db_name]
    
#     async def get_collection(self, db_name: str, collection_name: str):
#         """Get a collection from a database"""
#         db = await self.get_database(db_name)
#         return db[collection_name]

#     # CREATE
#     async def insert_one(self, db_name: str, collection_name: str, document: Dict) -> str:
#         """Insert a document into a collection and return the inserted ID"""
#         collection = await self.get_collection(db_name, collection_name)
#         document["created_at"] = datetime.now()
#         result = await collection.insert_one(document)
#         return str(result.inserted_id)
    
#     async def insert_many(self, db_name: str, collection_name: str, documents: List[Dict]) -> List[str]:
#         """Insert multiple documents into a collection and return the inserted IDs"""
#         collection = await self.get_collection(db_name, collection_name)
#         for doc in documents:
#             doc["created_at"] = datetime.now()
#         result = await collection.insert_many(documents)
#         return [str(id) for id in result.inserted_ids]
    
#     # READ
#     async def find_one(self, db_name: str, collection_name: str, query: Dict) -> Optional[Dict]:
#         """Find a single document in a collection"""
#         collection = await self.get_collection(db_name, collection_name)
#         document = await collection.find_one(query)
#         return document
    
#     async def find_by_id(self, db_name: str, collection_name: str, id: str) -> Optional[Dict]:
#         """Find a document by its ID"""
#         collection = await self.get_collection(db_name, collection_name)
#         document = await collection.find_one({"_id": ObjectId(id)})
#         return document
    
#     async def find_many(self, db_name: str, collection_name: str, query: Dict, 
#                   limit: int = 0, skip: int = 0, sort: Dict = None) -> List[Dict]:
#         """Find multiple documents in a collection with pagination and sorting options"""
#         collection = await self.get_collection(db_name, collection_name)
#         cursor = collection.find(query)
        
#         if skip:
#             cursor = cursor.skip(skip)
#         if limit:
#             cursor = cursor.limit(limit)
#         if sort:
#             cursor = cursor.sort(sort)
            
#         documents = await cursor.to_list(length=limit if limit else None)
#         return documents
    
#     # UPDATE
#     async def update_one(self, db_name: str, collection_name: str, query: Dict, update_data: Dict) -> int:
#         """Update a single document in a collection"""
#         collection = await self.get_collection(db_name, collection_name)
#         update_data["updated_at"] = datetime.now()
#         result = await collection.update_one(query, {"$set": update_data})
#         return result.modified_count
    
#     async def update_by_id(self, db_name: str, collection_name: str, id: str, update_data: Dict) -> int:
#         """Update a document by its ID"""
#         collection = await self.get_collection(db_name, collection_name)
#         update_data["updated_at"] = datetime.now()
#         result = await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
#         return result.modified_count
    
#     # DELETE
#     async def delete_one(self, db_name: str, collection_name: str, query: Dict) -> int:
#         """Delete a single document from a collection"""
#         collection = await self.get_collection(db_name, collection_name)
#         result = await collection.delete_one(query)
#         return result.deleted_count
    
#     async def delete_by_id(self, db_name: str, collection_name: str, id: str) -> int:
#         """Delete a document by its ID"""
#         collection = await self.get_collection(db_name, collection_name)
#         result = await collection.delete_one({"_id": ObjectId(id)})
#         return result.deleted_count
    
#     # UTILITY METHODS
#     async def count_documents(self, db_name: str, collection_name: str, query: Dict = {}) -> int:
#         """Count documents in a collection that match a query"""
#         collection = await self.get_collection(db_name, collection_name)
#         return await collection.count_documents(query)