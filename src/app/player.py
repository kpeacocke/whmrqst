from .inventory import Inventory, Item

class Player:
    def __init__(self, player_id, health, inventory_capacity=10):
        self.player_id = player_id
        self.health = health
        self.inventory = Inventory(inventory_capacity)

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def is_alive(self):
        return self.health > 0

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "health": self.health,
            "inventory": [{"name": item.name, "quantity": item.quantity} for item in self.inventory.items]
        }

    @staticmethod
    def from_dict(data):
        player = Player(
            player_id=data["player_id"], health=data["health"], inventory_capacity=10
        )
        for item_data in data["inventory"]:
            player.inventory.add_item(Item(item_data["name"], item_data["quantity"]))
        return player