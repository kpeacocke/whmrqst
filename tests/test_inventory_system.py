import pytest

# Mock Item class for representing items in the inventory
class Item:
    def __init__(self, name, stackable=False):
        self.name = name
        self.stackable = stackable

# Mock Inventory class for managing items
class Inventory:
    def __init__(self, max_capacity=10):
        self.items = {}  # Dictionary for inventory, key is item name, value is quantity
        self.max_capacity = max_capacity

    def add_item(self, item, quantity=1):
        """Add an item to the inventory. Stackable items increase quantity."""
        if item.name in self.items:
            # Check if adding items exceeds max capacity
            if self.get_total_items() + quantity > self.max_capacity:
                raise ValueError("Inventory capacity exceeded")
            self.items[item.name] += quantity
        else:
            if self.get_total_items() + quantity > self.max_capacity:
                raise ValueError("Inventory capacity exceeded")
            self.items[item.name] = quantity

    def remove_item(self, item_name, quantity=1):
        """Remove an item from the inventory. If it's a stackable item, decrease the quantity."""
        if item_name in self.items:
            if self.items[item_name] <= quantity:
                del self.items[item_name]
            else:
                self.items[item_name] -= quantity

    def use_item(self, item_name):
        """Simulate using a consumable item by removing one instance of it."""
        if item_name in self.items:
            self.remove_item(item_name, 1)
        else:
            raise ValueError("Item not found in inventory")

    def get_total_items(self):
        """Return the total number of items in the inventory."""
        return sum(self.items.values())

# Test cases for Inventory System

def test_add_item():
    # Scenario 1: Ensure items can be added to the inventory
    inventory = Inventory()
    sword = Item(name="Sword")
    
    inventory.add_item(sword)
    
    assert inventory.items["Sword"] == 1, "Inventory should have 1 Sword."

def test_remove_item():
    # Scenario 2: Ensure items can be removed from the inventory
    inventory = Inventory()
    potion = Item(name="Potion")
    
    inventory.add_item(potion, 3)
    inventory.remove_item("Potion", 2)
    
    assert inventory.items["Potion"] == 1, "There should be 1 Potion left after removing 2."

    inventory.remove_item("Potion", 1)
    assert "Potion" not in inventory.items, "Potion should be completely removed after using the last one."

def test_inventory_capacity():
    # Scenario 3: Ensure the inventory enforces a maximum capacity
    inventory = Inventory(max_capacity=5)
    sword = Item(name="Sword")
    potion = Item(name="Potion")
    
    inventory.add_item(sword, 2)
    inventory.add_item(potion, 3)
    
    with pytest.raises(ValueError, match="Inventory capacity exceeded"):
        inventory.add_item(sword, 1)  # Trying to exceed capacity by adding 1 more Sword

def test_item_stacking():
    # Scenario 4: Ensure stackable items can be added correctly
    inventory = Inventory()
    potion = Item(name="Potion", stackable=True)
    
    inventory.add_item(potion, 5)
    
    assert inventory.items["Potion"] == 5, "There should be 5 Potions stacked."

def test_use_consumable_item():
    # Scenario 5: Ensure consumable items can be used and removed from the inventory
    inventory = Inventory()
    potion = Item(name="Potion", stackable=True)
    
    inventory.add_item(potion, 3)
    inventory.use_item("Potion")
    
    assert inventory.items["Potion"] == 2, "There should be 2 Potions left after using 1."

    # Using the remaining potions
    inventory.use_item("Potion")
    inventory.use_item("Potion")
    
    assert "Potion" not in inventory.items, "All Potions should be used and removed from inventory."