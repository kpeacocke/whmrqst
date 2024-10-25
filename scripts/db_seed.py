import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone

# Get MongoDB credentials from environment variables
mongo_username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
mongo_host = os.getenv('MONGO_HOST', 'localhost')  # Default to localhost if not set
mongo_port = os.getenv('MONGO_PORT', '27017')      # Default to 27017 if not set
mongo_db_name = os.getenv('MONGO_DB_NAME', 'game_database')

# Construct the MongoDB connection string
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db_name}?authSource=admin"

# MongoDB connection setup
client = MongoClient(mongo_uri)
db = client[mongo_db_name]

# Check if collections are empty before seeding
if db.players.count_documents({}) == 0 and db.quests.count_documents({}) == 0:
    # Define initial data for seeding
    current_time = datetime.now(timezone.utc)  # Use timezone-aware datetime in UTC

    players = [
        {
            "player_id": "1234",
            "health": 100,
            "inventory": [
                {"name": "Sword", "quantity": 1},
                {"name": "Health Potion", "quantity": 5}
            ],
            "quests": [
                {"quest_id": ObjectId(), "name": "Find the Sword", "status": "Not Started"},
                {"quest_id": ObjectId(), "name": "Defeat the Dragon", "status": "In Progress"}
            ],
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "player_id": "5678",
            "health": 80,
            "inventory": [
                {"name": "Bow", "quantity": 1},
                {"name": "Arrows", "quantity": 10}
            ],
            "quests": [
                {"quest_id": ObjectId(), "name": "Find the Ancient Relic", "status": "Not Started"}
            ],
            "created_at": current_time,
            "updated_at": current_time
        }
    ]

    quests = [
        {
            "quest_id": ObjectId(),
            "name": "Find the Sword",
            "description": "You must locate the legendary sword to defeat the dark wizard.",
            "reward": "100 Gold",
            "stages": ["Search the forest", "Find the village elder", "Retrieve the sword"],
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "quest_id": ObjectId(),
            "name": "Defeat the Dragon",
            "description": "Slay the dragon terrorizing the kingdom.",
            "reward": "Dragon's Hoard",
            "stages": ["Reach the mountain", "Defeat the dragon", "Return to the king"],
            "created_at": current_time,
            "updated_at": current_time
        }
    ]

    # Insert the data into the MongoDB collections
    db.players.insert_many(players)
    db.quests.insert_many(quests)

    print("Database seeded successfully with players and quests.")
else:
    print("Database already seeded. No action taken.")