import os

# MongoDB configuration
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "secure_password")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo_prod")  # Defaults to 'mongo_prod'; set to 'mongo_debug' for debugging
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "game_database")

# Build the Mongo URI dynamically
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource=admin"

# Application secret key for session management
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Provide a secure key in the environment