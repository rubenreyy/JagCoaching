import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
load_dotenv("./.env.development")

import uuid


class CloudDBController:
    """Class to handle MongoDB operations"""

    def __init__(self):
        # Get the URI from the environment variables
        db_cloud_username = os.getenv("DB_CLOUD_USERNAME")
        db_cloud_password = os.getenv("DB_CLOUD_PASSWORD")
        self.uri = os.getenv(
            "MONGO_URI", f"mongodb+srv://{db_cloud_username}:{db_cloud_password}@cluster0.i148f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = MongoClient(self.uri, server_api=ServerApi('1'), connect=False)

    def connect(self):
        """Connect to the MongoDB client"""
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Connection failed: {e}")
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

    # -------------------
    # Phase 1: Refresh Tokens
    # -------------------
    def save_refresh_token(self, db_name, token_data):
        """Save a refresh token to the database"""
        return self.client[db_name]["refresh_tokens"].insert_one(token_data)

    def get_refresh_token(self, db_name, token_hash):
        """Retrieve a refresh token by its hash"""
        return self.client[db_name]["refresh_tokens"].find_one({"token_hash": token_hash})

    def delete_refresh_token(self, db_name, token_hash):
        """Delete a specific refresh token"""
        return self.client[db_name]["refresh_tokens"].delete_one({"token_hash": token_hash})

    def delete_all_refresh_tokens_for_user(self, db_name, user_id):
        """Delete all refresh tokens for a specific user"""
        return self.client[db_name]["refresh_tokens"].delete_many({"user_id": user_id})

    # -------------------
    # Phase 2: Revocation
    # -------------------
    def revoke_token(self, db_name, token, expires_at, reason=None):
        """Revoke a token by adding it to the revoked_tokens collection"""
        return self.client[db_name]["revoked_tokens"].insert_one({
            "token": token,
            "expires_at": expires_at,
            "reason": reason,
            "revoked_at": datetime.utcnow(),
            "type": "revoked"
        })

    def is_token_revoked(self, db_name, token):
        """Check if a token has been revoked"""
        return self.client[db_name]["revoked_tokens"].find_one({"token": token})

    # -------------------
    # Phase 3: Blacklisting
    # -------------------
    def blacklist_token(self, db_name, token, expires_at, reason="blacklisted"):
        """Blacklist a token with a specific reason"""
        return self.client[db_name]["revoked_tokens"].insert_one({
            "token": token,
            "expires_at": expires_at,
            "reason": reason,
            "revoked_at": datetime.utcnow(),
            "type": "blacklist"
        })

    def cleanup_expired_blacklist_tokens(self, db_name):
        """Remove expired tokens from the blacklist"""
        now = datetime.utcnow()
        return self.client[db_name]["revoked_tokens"].delete_many({
            "expires_at": {"$lte": now},
            "type": "blacklist"
        })

    # -------------------
    # Phase 4: Session Management
    # -------------------
    def create_session(self, db_name, session_data):
        """Create a new user session"""
        return self.client[db_name]["sessions"].insert_one(session_data)

    def get_sessions_for_user(self, db_name, user_id):
        """Get all active sessions for a user"""
        return list(self.client[db_name]["sessions"].find({"user_id": user_id}))

    def delete_session(self, db_name, session_id):
        """Delete a specific session"""
        return self.client[db_name]["sessions"].delete_one({"session_id": session_id})

    def delete_all_sessions_for_user(self, db_name, user_id):
        """Delete all sessions for a specific user"""
        return self.client[db_name]["sessions"].delete_many({"user_id": user_id})

    def revoke_all_user_tokens(self, db_name, user_id, reason="password_change"):
        """Revoke all refresh tokens for a user (cascade revocation)"""
        try:
            # Find all refresh tokens for the user
            refresh_tokens = self.client[db_name]["refresh_tokens"].find({"user_id": user_id})
            
            # Add all tokens to the revoked list
            for token_doc in refresh_tokens:
                token_hash = token_doc.get("token_hash")
                expires_at = token_doc.get("expires_at")
                
                if token_hash and expires_at:
                    self.client[db_name]["revoked_tokens"].insert_one({
                        "token_hash": token_hash,
                        "user_id": user_id,
                        "revoked_at": datetime.now(),
                        "expires_at": expires_at,
                        "reason": reason
                    })
            
            # Delete all refresh tokens for the user
            result = self.client[db_name]["refresh_tokens"].delete_many({"user_id": user_id})
            
            # Also terminate all sessions
            self.client[db_name]["sessions"].delete_many({"user_id": user_id})
            
            return result.deleted_count
        except Exception as e:
            print(f"Error revoking all user tokens: {str(e)}")
            return 0

    def create_user_session(self, db_name, user_id, ip_address, device_info, location=None):
        """Create a new user session with enhanced analytics"""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Attempt to get geolocation data if not provided
            if not location and ip_address and ip_address != "unknown" and ip_address != "127.0.0.1":
                # This would typically use a GeoIP service
                # For now, we'll just use a placeholder
                location = {"country": "Unknown", "city": "Unknown"}
            
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "device_info": device_info,
                "created_at": now,
                "last_active": now,
                "location": location,
                "login_count": 1,
                "activity_log": [{
                    "action": "session_created",
                    "timestamp": now,
                    "ip_address": ip_address
                }]
            }
            
            self.client[db_name]["sessions"].insert_one(session)
            return session_id
        except Exception as e:
            print(f"Error creating user session: {str(e)}")
            return None

    def update_session_activity(self, db_name, session_id, action="page_view", details=None):
        """Update session activity with detailed analytics"""
        try:
            now = datetime.now()
            
            # Add activity to log
            activity = {
                "action": action,
                "timestamp": now
            }
            
            if details:
                activity["details"] = details
            
            self.client[db_name]["sessions"].update_one(
                {"session_id": session_id},
                {
                    "$set": {"last_active": now},
                    "$inc": {"login_count": 1 if action == "login" else 0},
                    "$push": {"activity_log": activity}
                }
            )
            return True
        except Exception as e:
            print(f"Error updating session activity: {str(e)}")
            return False

    def get_user_session_analytics(self, db_name, user_id):
        """Get detailed session analytics for a user"""
        try:
            # Get all sessions for the user
            sessions = list(self.client[db_name]["sessions"].find(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            ))
            
            # Calculate analytics
            total_sessions = len(sessions)
            active_sessions = sum(1 for s in sessions if (datetime.now() - s.get("last_active", datetime.min)).total_seconds() < 3600)
            
            devices = {}
            locations = {}
            login_times = []
            
            for session in sessions:
                # Track devices
                device = "Unknown"
                if session.get("device_info") and session.get("device_info").get("user_agent"):
                    ua = session["device_info"]["user_agent"]
                    if "Mobile" in ua:
                        device = "Mobile"
                    elif "Tablet" in ua:
                        device = "Tablet"
                    else:
                        device = "Desktop"
                devices[device] = devices.get(device, 0) + 1
                
                # Track locations
                location = "Unknown"
                if session.get("location") and session.get("location").get("country"):
                    location = session["location"]["country"]
                locations[location] = locations.get(location, 0) + 1
                
                # Track login times
                if session.get("created_at"):
                    login_times.append(session["created_at"])
            
            # Analyze login patterns by hour of day
            hour_distribution = {}
            for login_time in login_times:
                hour = login_time.hour
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "devices": devices,
                "locations": locations,
                "hour_distribution": hour_distribution,
                "recent_sessions": sessions[:5]  # Return the 5 most recent sessions
            }
        except Exception as e:
            print(f"Error getting user session analytics: {str(e)}")
            return {}

    def record_security_event(self, db_name, event_data):
        """Record a security event for auditing and monitoring"""
        try:
            # Ensure the security_events collection exists
            if "security_events" not in self.client[db_name].list_collection_names():
                self.client[db_name].create_collection("security_events")
                # Create index on user_id and timestamp for faster queries
                self.client[db_name]["security_events"].create_index([("user_id", 1), ("timestamp", -1)])
            
            # Add timestamp if not provided
            if "timestamp" not in event_data:
                event_data["timestamp"] = datetime.now()
            
            result = self.client[db_name]["security_events"].insert_one(event_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error recording security event: {str(e)}")
            return None

    def get_user_recent_sessions(self, db_name, user_id, limit=5):
        """Get the most recent sessions for a user"""
        try:
            return list(self.client[db_name]["sessions"].find(
                {"user_id": user_id},
                sort=[("created_at", -1)],
                limit=limit
            ))
        except Exception as e:
            print(f"Error getting recent user sessions: {str(e)}")
            return []


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
