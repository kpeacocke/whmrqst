from . import mongo


def init_db(app):
    mongo.init_app(app)


# Database operations
def _player_collection():
    database = mongo.db
    if database is None:
        raise RuntimeError("MongoDB has not been initialized")
    return database.players


def get_player(player_id):
    return _player_collection().find_one({"player_id": player_id})


def save_player(player_data):
    return _player_collection().update_one(
        {"player_id": player_data["player_id"]}, {"$set": player_data}, upsert=True
    )
