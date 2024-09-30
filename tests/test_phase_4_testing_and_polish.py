import pytest

# Mock classes for UI and System Polish

class UI:
    def __init__(self):
        self.displayed_items = []
        self.displayed_health = 100

    def update_inventory(self, inventory):
        """Update the UI to display the current inventory."""
        self.displayed_items = [item.name for item in inventory.items]

    def update_health(self, player):
        """Update the health bar to reflect the player's health."""
        self.displayed_health = player.health


class Player:
    def __init__(self, health):
        self.health = health
        self.inventory = Inventory(capacity=10)

    def take_damage(self, amount):
        """Reduce player's health."""
        self.health = max(0, self.health - amount)


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        """Add an item to the inventory if there's space."""
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item_name):
        """Remove an item by name."""
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                return True
        return False


class Item:
    def __init__(self, name):
        self.name = name


# Test cases for Phase 4 Testing and Polish

# UI Polish

def test_inventory_ui_update():
    # Ensure the UI correctly updates when items are added or removed
    inventory = Inventory(capacity=5)
    sword = Item(name="Sword")
    shield = Item(name="Shield")
    
    ui = UI()
    inventory.add_item(sword)
    inventory.add_item(shield)
    
    ui.update_inventory(inventory)
    
    assert ui.displayed_items == ["Sword", "Shield"], "UI should display 'Sword' and 'Shield' in inventory."

    # Now remove the shield and check the UI again
    inventory.remove_item("Shield")
    ui.update_inventory(inventory)
    
    assert ui.displayed_items == ["Sword"], "UI should display only 'Sword' after Shield is removed."

def test_health_ui_update():
    # Ensure the UI health bar updates correctly when the player takes damage
    player = Player(health=100)
    ui = UI()
    
    player.take_damage(30)
    ui.update_health(player)
    
    assert ui.displayed_health == 70, "Health UI should display 70 after player takes 30 damage."

    player.take_damage(80)
    ui.update_health(player)
    
    assert ui.displayed_health == 0, "Health UI should display 0 after player's health is reduced to 0."

# Edge Case Handling

def test_empty_inventory_ui():
    # Ensure UI handles an empty inventory
    inventory = Inventory(capacity=5)
    ui = UI()
    
    ui.update_inventory(inventory)
    assert ui.displayed_items == [], "UI should display an empty inventory when there are no items."

def test_inventory_full():
    # Ensure that inventory behaves correctly when full
    inventory = Inventory(capacity=2)
    sword = Item(name="Sword")
    shield = Item(name="Shield")
    potion = Item(name="Potion")
    
    assert inventory.add_item(sword), "Sword should be added."
    assert inventory.add_item(shield), "Shield should be added."
    assert not inventory.add_item(potion), "Potion should not be added because inventory is full."

# Performance Testing Under Load

def test_inventory_performance_under_load():
    # Simulate adding a large number of items to the inventory and ensure no performance issues
    inventory = Inventory(capacity=1000)
    ui = UI()
    
    for i in range(1000):
        inventory.add_item(Item(name=f"Item_{i}"))
    
    ui.update_inventory(inventory)
    
    assert len(ui.displayed_items) == 1000, "UI should correctly display 1000 items in the inventory."
    assert inventory.items[-1].name == "Item_999", "The last item should be 'Item_999'."

# Input Handling

def test_invalid_input_movement():
    # Ensure the player cannot move out of bounds or perform invalid actions
    # For example, let's assume the game has defined bounds (e.g., x, y coordinates).
    def move_player(x, y):
        if x < 0 or y < 0:
            return "Invalid Move"
        return f"Player moved to ({x}, {y})"

    assert move_player(-1, 5) == "Invalid Move", "Player should not be able to move to negative coordinates."
    assert move_player(10, -3) == "Invalid Move", "Player should not be able to move to negative coordinates."

def test_invalid_inventory_item_removal():
    # Ensure removing an item that isn't in the inventory doesn't cause issues
    inventory = Inventory(capacity=5)
    sword = Item(name="Sword")
    
    assert not inventory.remove_item("NonExistentItem"), "Trying to remove an item not in the inventory should return False."
    inventory.add_item(sword)
    assert inventory.remove_item("Sword"), "Sword should be successfully removed."