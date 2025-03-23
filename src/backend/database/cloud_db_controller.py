import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
load_dotenv("./.env.development")



class CloudMongoDBController(MongoClient):
    def __init__(self):
        # Get the URI from the environment variables
        db_cloud_password = os.getenv("DB_CLOUD_PASSWORD")
        self.uri = os.getenv("MONGO_DB_URI")
        self.client = self.connect()

class CloudDBController:
    """Class to handle MongoDB operations"""

    def __init__(self):
        # Get the URI from the environment variables
        db_cloud_password = os.getenv("DB_CLOUD_PASSWORD")
        self.uri = os.getenv(
            "MONGO_URI", f"mongodb+srv://chnast01:{db_cloud_password}@cluster0.i148f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = self.connect()

    def connect(self):
        """Connect to the MongoDB client"""
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except ConnectionError as e:
            print(e)
        return self.client

    def get_database(self, db_name):
        """ Get a database from the client """
        return self.client[db_name]

    def get_collection(self, db_name, collection_name):
        """ Get a collection from the database """
        return self.client[db_name][collection_name]

    def add_document(self, db_name, collection_name, document) -> InsertOneResult:
        """Add a document to the collection"""
        return self.client[db_name][collection_name].insert_one(document)

    def update_document(self, db_name, collection_name, filter_dict, update_dict) -> UpdateResult:
        """Update a document in the collection based on filter criteria"""
        return self.client[db_name][collection_name].update_one(filter_dict, {"$set": update_dict})

    def delete_document(self, db_name, collection_name, filter_dict):
        """Delete a document from the collection based on filter criteria"""
        return self.client[db_name][collection_name].delete_one(filter_dict)

    def find_document(self, db_name, collection_name, filter_dict):
        """Find a single document in the collection based on filter criteria"""
        return self.client[db_name][collection_name].find_one(filter_dict)

    def find_documents(self, db_name, collection_name, filter_dict=None, projection=None, limit=0):
        """Find multiple documents in the collection based on filter criteria"""
        return list(self.client[db_name][collection_name].find(
            filter_dict or {}, projection, limit=limit
        ))

    def aggregate(self, db_name, collection_name, pipeline):
        """Perform an aggregation operation on the collection"""
        return list(self.client[db_name][collection_name].aggregate(pipeline))

    def bulk_insert(self, db_name, collection_name, documents):
        """Insert multiple documents at once"""
        return self.client[db_name][collection_name].insert_many(documents)

    def count_documents(self, db_name, collection_name, filter_dict=None):
        """Count documents matching the filter criteria"""
        return self.client[db_name][collection_name].count_documents(filter_dict or {})


class CloudDBInitializer(CloudDBController):
    """Class to initialize the MongoDB database with collections and indexes"""

    def create_collections_and_indexes(self):
        """Create the necessary collections and indexes for the application"""
        db_controller = CloudDBController()

        # Create users collection
        users_db = db_controller.get_database("JagCoaching")
        users_collection = users_db["users"]

        # Create videos collection
        videos_collection = users_db["videos"]

        # Create indexes
        users_collection.create_index("email", unique=True)
        # For faster queries on user's videos
        videos_collection.create_index("user_id")
        videos_collection.create_index("upload_date")  # For sorting by date

        print("Collections and indexes created successfully!")

        return users_collection, videos_collection

    def add_sample_data(self):
        """Add some sample data to test the collections"""

        # Add a sample user
        user = {
            "email": "user@example.com",
            "name": "Test User",
            "created_at": datetime.now(),
        }

        result = self.add_document("JagCoaching", "users", user)
        user_id = str(result.inserted_id)

        # Add a sample video linked to the user
        video = {
            "title": "Sample Coaching Video",
            "description": "A test video for the coaching platform",
            "tags": ["interview", "practice"],
            "user_id": user_id,
            "file_path": "/videos/sample.mp4",
            "upload_date": datetime.now(),
            "size_bytes": 10000000
        }

        self.add_document("JagCoaching", "videos", video)

        print(f"Sample data added for user {user_id}")


def main():

    db_initializer = CloudDBInitializer()
    # db_initializer.create_collections_and_indexes()
    # db_initializer.add_sample_data()

    print("Initialization complete!")
    print(db_initializer.get_collection("JagCoaching", "users").find_one())
    print(db_initializer.get_collection("JagCoaching", "videos").find_one())


if __name__ == "__main__":
    main()
