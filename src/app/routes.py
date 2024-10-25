from flask import Blueprint, jsonify, request, render_template
from .models import get_player, save_player
from .player import Player
from .inventory import Item

main = Blueprint('main', __name__)

# Define a constant for the "Player not found" message
PLAYER_NOT_FOUND = "Player not found"

# Root route for the homepage
@main.route('/')
def index():
    """Render the game dashboard."""
    return render_template('index.html')

@main.route("/player/<player_id>", methods=["GET"])
def get_player_info(player_id):
    """Retrieve player info."""
    player_data = get_player(player_id)
    if player_data:
        player = Player.from_dict(player_data)
        return jsonify(player.to_dict())
    return jsonify({"error": PLAYER_NOT_FOUND}), 404

@main.route("/player/<player_id>/add_item", methods=["POST"])
def add_item_to_inventory(player_id):
    """Add an item to the player's inventory."""
    player_data = get_player(player_id)
    if not player_data:
        return jsonify({"error": PLAYER_NOT_FOUND}), 404

    player = Player.from_dict(player_data)
    item_name = request.json.get("item_name")
    quantity = request.json.get("quantity", 1)

    item = Item(name=item_name, quantity=quantity)
    player.inventory.add_item(item)

    save_player(player.to_dict())
    return jsonify(player.to_dict())

@main.route("/player/<player_id>/take_damage", methods=["POST"])
def player_take_damage(player_id):
    """Apply damage to the player."""
    player_data = get_player(player_id)
    if not player_data:
        return jsonify({"error": PLAYER_NOT_FOUND}), 404

    player = Player.from_dict(player_data)
    damage = request.json.get("damage", 10)
    player.take_damage(damage)

    save_player(player.to_dict())
    return jsonify(player.to_dict())

@main.route("/player/<player_id>/heal", methods=["POST"])
def player_heal(player_id):
    """Heal the player."""
    player_data = get_player(player_id)
    if not player_data:
        return jsonify({"error": PLAYER_NOT_FOUND}), 404

    player = Player.from_dict(player_data)
    heal_amount = request.json.get("heal", 10)
    player.heal(heal_amount)

    save_player(player.to_dict())
    return jsonify(player.to_dict())