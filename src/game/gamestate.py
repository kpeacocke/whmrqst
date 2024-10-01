from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['game_database']

# Drop collections to clean the database before seeding
db.players.drop()
db.quests.drop()

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