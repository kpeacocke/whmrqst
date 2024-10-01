from . import mongo

def init_db(app):
    mongo.init_app(app)

# Database operations
def get_player(player_id):
    return mongo.db.players.find_one({"player_id": player_id})

def save_player(player_data):
    return mongo.db.players.update_one(
        {"player_id": player_data["player_id"]}, {"$set": player_data}, upsert=True
    )