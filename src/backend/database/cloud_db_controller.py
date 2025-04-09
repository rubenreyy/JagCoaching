import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
load_dotenv("./.env.development")


class CloudDBController:
    """Class to handle MongoDB operations"""

    def __init__(self):
        db_cloud_username = os.getenv("DB_CLOUD_USERNAME")
        db_cloud_password = os.getenv("DB_CLOUD_PASSWORD")
        self.uri = os.getenv(
            "MONGO_URI", f"mongodb+srv://{db_cloud_username}:{db_cloud_password}@cluster0.i148f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = MongoClient(self.uri, server_api=ServerApi('1'), connect=False)

    def connect(self):
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Connection failed: {e}")
        return self.client

    def get_database(self, db_name):
        return self.client[db_name]

    def get_collection(self, db_name, collection_name):
        return self.client[db_name][collection_name]

    def add_document(self, db_name, collection_name, document) -> InsertOneResult:
        return self.client[db_name][collection_name].insert_one(document)

    def update_document(self, db_name, collection_name, filter_dict, update_dict) -> UpdateResult:
        return self.client[db_name][collection_name].update_one(filter_dict, {"$set": update_dict})

    def delete_document(self, db_name, collection_name, filter_dict):
        return self.client[db_name][collection_name].delete_one(filter_dict)

    def find_document(self, db_name, collection_name, filter_dict):
        return self.client[db_name][collection_name].find_one(filter_dict)

    def find_documents(self, db_name, collection_name, filter_dict=None, projection=None, limit=0):
        return list(self.client[db_name][collection_name].find(
            filter_dict or {}, projection, limit=limit
        ))

    def aggregate(self, db_name, collection_name, pipeline):
        return list(self.client[db_name][collection_name].aggregate(pipeline))

    def bulk_insert(self, db_name, collection_name, documents):
        return self.client[db_name][collection_name].insert_many(documents)

    def count_documents(self, db_name, collection_name, filter_dict=None):
        return self.client[db_name][collection_name].count_documents(filter_dict or {})

    # April 1 // Phase 1: Refresh Token Handling Methods
    def save_refresh_token(self, db_name, token_data):
        return self.client[db_name]["refresh_tokens"].insert_one(token_data)

    def get_refresh_token(self, db_name, token_hash):
        return self.client[db_name]["refresh_tokens"].find_one({"token_hash": token_hash})

    def delete_refresh_token(self, db_name, token_hash):
        return self.client[db_name]["refresh_tokens"].delete_one({"token_hash": token_hash})

    def delete_all_refresh_tokens_for_user(self, db_name, user_id):
        return self.client[db_name]["refresh_tokens"].delete_many({"user_id": user_id})

    # April 1 // Phase 2: Token Revocation Methods
    def revoke_token(self, db_name, token, expires_at, reason=None):
        return self.client[db_name]["revoked_tokens"].insert_one({
            "token": token,
            "expires_at": expires_at,
            "reason": reason,
            "revoked_at": datetime.utcnow(),
            "type": "revoked"
        })

    def is_token_revoked(self, db_name, token):
        return self.client[db_name]["revoked_tokens"].find_one({"token": token})

    # April 2 // Phase 3: Token Blacklisting Methods
    def blacklist_token(self, db_name, token, expires_at, reason="blacklisted"):
        return self.client[db_name]["revoked_tokens"].insert_one({
            "token": token,
            "expires_at": expires_at,
            "reason": reason,
            "revoked_at": datetime.utcnow(),
            "type": "blacklist"
        })

    def cleanup_expired_blacklist_tokens(self, db_name):
        now = datetime.utcnow()
        return self.client[db_name]["revoked_tokens"].delete_many({
            "expires_at": {"$lte": now},
            "type": "blacklist"
        })

    #  April 8 // Phase 4: Session Management Methods
    def create_session(self, db_name, session_data):
        return self.client[db_name]["sessions"].insert_one(session_data)

    def get_sessions_by_user(self, db_name, user_id):
        return list(self.client[db_name]["sessions"].find({"user_id": user_id}))

    def terminate_session(self, db_name, session_id):
        return self.client[db_name]["sessions"].delete_one({"_id": session_id})

    def terminate_all_sessions(self, db_name, user_id):
        return self.client[db_name]["sessions"].delete_many({"user_id": user_id})

    def cleanup_expired_sessions(self, db_name, cutoff_time):
        return self.client[db_name]["sessions"].delete_many({"last_active": {"$lt": cutoff_time}})


class CloudDBInitializer(CloudDBController):
    def create_collections_and_indexes(self):
        db_controller = CloudDBController()
        users_db = db_controller.get_database("JagCoaching")
        users_collection = users_db["users"]
        videos_collection = users_db["videos"]
        users_collection.create_index("email", unique=True)
        videos_collection.create_index("user_id")
        videos_collection.create_index("upload_date")
        print("Collections and indexes created successfully!")
        return users_collection, videos_collection

    def add_sample_data(self):
        user = {
            "email": "user@example.com",
            "name": "Test User",
            "created_at": datetime.now(),
        }
        result = self.add_document("JagCoaching", "users", user)
        user_id = str(result.inserted_id)
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
