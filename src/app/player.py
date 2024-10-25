from .inventory import Inventory, Item

class Player:
    def __init__(self, player_id, health, inventory_capacity=10, max_health=None):
        self.player_id = player_id
        self.health = health
        self.max_health = max_health  # Optional maximum health limit
        self.inventory = Inventory(inventory_capacity)

    def take_damage(self, damage):
        """Reduce the player's health by the given damage amount."""
        self.health = max(0, self.health - damage)

    def heal(self, amount):
        """Heal the player by the given amount, respecting max health if set."""
        self.health += amount
        if self.max_health is not None:
            self.health = min(self.health, self.max_health)

    def is_alive(self):
        """Check if the player is still alive."""
        return self.health > 0

    def to_dict(self):
        """Serialize the player object to a dictionary."""
        return {
            "player_id": self.player_id,
            "health": self.health,
            "inventory": [item.to_dict() for item in self.inventory.items]
        }

    @staticmethod
    def from_dict(data):
        """Create a Player object from a dictionary."""
        inventory_capacity = data.get("inventory_capacity", 10)
        max_health = data.get("max_health")  # Optional field
        player = Player(
            player_id=data["player_id"],
            health=data["health"],
            inventory_capacity=inventory_capacity,
            max_health=max_health
        )
        for item_data in data["inventory"]:
            player.inventory.add_item(Item(item_data["name"], item_data["quantity"]))
        return player