import pytest

# Mock classes for Inventory and Crafting Systems

class Item:
    def __init__(self, name, quantity=1):
        self.name = name
        self.quantity = quantity

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
        """Remove an item by name from the inventory."""
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                return True
        return False

    def get_item(self, item_name):
        """Return an item from the inventory by name."""
        for item in self.items:
            if item.name == item_name:
                return item
        return None

    def has_items(self, required_items):
        """Check if the inventory has all the required items."""
        for req_item, req_qty in required_items.items():
            item = self.get_item(req_item)
            if not item or item.quantity < req_qty:
                return False
        return True

    def remove_items(self, items_to_remove):
        """Remove multiple items from the inventory."""
        for item_name, qty in items_to_remove.items():
            item = self.get_item(item_name)
            if item:
                if item.quantity > qty:
                    item.quantity -= qty
                else:
                    self.items.remove(item)

class CraftingSystem:
    def __init__(self, recipes):
        self.recipes = recipes  # Dictionary of recipes

    def craft(self, inventory, recipe_name):
        """Craft an item if the player has the required materials."""
        if recipe_name not in self.recipes:
            return None  # Recipe does not exist

        recipe = self.recipes[recipe_name]
        if inventory.has_items(recipe["materials"]):
            inventory.remove_items(recipe["materials"])
            crafted_item = Item(recipe["result"], quantity=recipe.get("quantity", 1))
            inventory.add_item(crafted_item)
            return crafted_item
        return None


# Test cases for Phase 3 Inventory and Crafting Systems

# Inventory Management

def test_add_item_to_inventory():
    # Ensure that items can be added to the inventory
    inventory = Inventory(capacity=5)
    
    sword = Item(name="Sword")
    shield = Item(name="Shield")
    
    assert inventory.add_item(sword), "Sword should be added to the inventory."
    assert inventory.add_item(shield), "Shield should be added to the inventory."
    
    assert len(inventory.items) == 2, "Inventory should contain two items."

def test_remove_item_from_inventory():
    # Ensure that items can be removed from the inventory
    inventory = Inventory(capacity=5)
    
    potion = Item(name="Potion")
    inventory.add_item(potion)
    
    assert inventory.remove_item("Potion"), "Potion should be removed from the inventory."
    assert len(inventory.items) == 0, "Inventory should be empty after removing the item."

def test_inventory_capacity_limit():
    # Ensure that items cannot be added when inventory is full
    inventory = Inventory(capacity=2)
    
    item1 = Item(name="Sword")
    item2 = Item(name="Shield")
    item3 = Item(name="Helmet")
    
    assert inventory.add_item(item1), "Sword should be added."
    assert inventory.add_item(item2), "Shield should be added."
    assert not inventory.add_item(item3), "Helmet should not be added as inventory is full."
    
    assert len(inventory.items) == 2, "Inventory should contain only two items."

# Crafting System

def test_craft_item_success():
    # Ensure that items can be crafted if materials are available
    inventory = Inventory(capacity=5)
    inventory.add_item(Item(name="Wood", quantity=3))
    inventory.add_item(Item(name="Iron", quantity=2))
    
    recipes = {
        "Sword": {
            "materials": {"Wood": 1, "Iron": 2},
            "result": "Sword",
        }
    }
    
    crafting_system = CraftingSystem(recipes)
    crafted_item = crafting_system.craft(inventory, "Sword")
    
    assert crafted_item is not None, "Sword should be crafted."
    assert crafted_item.name == "Sword", "Crafted item should be a Sword."
    assert inventory.get_item("Wood").quantity == 2, "Wood quantity should decrease after crafting."
    assert inventory.get_item("Iron") is None, "All Iron should be consumed after crafting."

def test_craft_item_insufficient_materials():
    # Ensure that crafting fails if materials are insufficient
    inventory = Inventory(capacity=5)
    inventory.add_item(Item(name="Wood", quantity=1))
    inventory.add_item(Item(name="Iron", quantity=1))
    
    recipes = {
        "Sword": {
            "materials": {"Wood": 1, "Iron": 2},
            "result": "Sword",
        }
    }
    
    crafting_system = CraftingSystem(recipes)
    crafted_item = crafting_system.craft(inventory, "Sword")
    
    assert crafted_item is None, "Sword should not be crafted due to insufficient Iron."
    assert inventory.get_item("Wood").quantity == 1, "No materials should be consumed on crafting failure."
    assert inventory.get_item("Iron").quantity == 1, "No Iron should be consumed on crafting failure."

def test_craft_item_inventory_full():
    # Ensure crafting fails if there's no space in inventory for the crafted item
    inventory = Inventory(capacity=2)
    inventory.add_item(Item(name="Wood", quantity=3))
    inventory.add_item(Item(name="Iron", quantity=2))
    
    # Inventory full with other items
    inventory.add_item(Item(name="Shield"))
    
    recipes = {
        "Sword": {
            "materials": {"Wood": 1, "Iron": 2},
            "result": "Sword",
        }
    }
    
    crafting_system = CraftingSystem(recipes)
    crafted_item = crafting_system.craft(inventory, "Sword")
    
    assert crafted_item is None, "Sword should not be crafted because inventory is full."