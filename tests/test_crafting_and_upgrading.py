import pytest

# Mock Item class for crafting and upgrading
class Item:
    def __init__(self, name, base_power=10, upgrade_level=0):
        self.name = name
        self.base_power = base_power
        self.upgrade_level = upgrade_level

    def upgrade(self):
        # Each upgrade increases base power by 5
        self.upgrade_level += 1
        self.base_power += 5

# Mock Character class with inventory
class Character:
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.resources = {"gold": 100, "materials": 50}

    def add_item(self, item):
        self.inventory.append(item)

    def has_item(self, item_name):
        return any(item.name == item_name for item in self.inventory)

    def remove_resources(self, gold, materials):
        if self.resources["gold"] >= gold and self.resources["materials"] >= materials:
            self.resources["gold"] -= gold
            self.resources["materials"] -= materials
            return True
        return False

# Mock CraftingSystem class for handling crafting and upgrading
class CraftingSystem:
    def __init__(self):
        # No initialization needed for now, may be extended later
        pass

    def craft(self, char, item_name, required_gold, required_materials):
        # Simple crafting logic: consume resources and add the item to the inventory
        if char.remove_resources(required_gold, required_materials):
            new_item = Item(name=item_name)
            char.add_item(new_item)
            return new_item
        else:
            raise ValueError("Insufficient resources for crafting.")

    def upgrade(self, char, item_name, required_gold, required_materials):
        # Find the item and upgrade it
        for item in char.inventory:
            if item.name == item_name:
                if char.remove_resources(required_gold, required_materials):
                    item.upgrade()
                    return item
                else:
                    raise ValueError("Insufficient resources for upgrading.")
        raise ValueError(f"Item {item_name} not found in inventory.")


# Test cases for Crafting and Upgrading

def test_crafting_new_item():
    # Scenario 1: Ensure crafting a new item works correctly
    char = Character(name="Hero")
    crafting_system = CraftingSystem()

    # Craft a sword
    crafted_item = crafting_system.craft(char, item_name="Sword", required_gold=20, required_materials=10)
    
    assert crafted_item.name == "Sword", "Crafted item should be 'Sword'."
    assert char.has_item("Sword"), "Character should have 'Sword' in inventory."
    assert char.resources["gold"] == 80, "Gold should decrease by 20."
    assert char.resources["materials"] == 40, "Materials should decrease by 10."

def test_upgrading_item():
    # Scenario 2: Ensure upgrading an item improves its stats
    char = Character(name="Hero")
    sword = Item(name="Sword", base_power=10)
    char.add_item(sword)
    crafting_system = CraftingSystem()

    # Upgrade the sword
    upgraded_item = crafting_system.upgrade(char, item_name="Sword", required_gold=30, required_materials=20)
    
    assert upgraded_item.base_power == 15, "Sword power should increase by 5 after upgrade."
    assert upgraded_item.upgrade_level == 1, "Sword upgrade level should be 1 after upgrade."
    assert char.resources["gold"] == 70, "Gold should decrease by 30."
    assert char.resources["materials"] == 30, "Materials should decrease by 20."

def test_insufficient_resources_for_crafting():
    # Scenario 3: Ensure crafting fails with insufficient resources
    char = Character(name="Hero")
    crafting_system = CraftingSystem()

    # Try to craft with insufficient materials
    with pytest.raises(ValueError, match="Insufficient resources for crafting."):
        crafting_system.craft(char, item_name="Sword", required_gold=200, required_materials=100)

def test_insufficient_resources_for_upgrading():
    # Scenario 4: Ensure upgrading fails with insufficient resources
    char = Character(name="Hero")
    sword = Item(name="Sword", base_power=10)
    char.add_item(sword)
    crafting_system = CraftingSystem()

    # Try to upgrade the sword with insufficient resources
    with pytest.raises(ValueError, match="Insufficient resources for upgrading."):
        crafting_system.upgrade(char, item_name="Sword", required_gold=200, required_materials=100)

def test_crafting_invalid_item():
    # Scenario 5: Ensure that attempting to craft an invalid item is handled correctly
    char = Character(name="Hero")
    crafting_system = CraftingSystem()

    # Trying to craft a non-existent item should raise a generic exception (you can expand this logic)
    with pytest.raises(ValueError, match="Insufficient resources for crafting."):
        crafting_system.craft(char, item_name="Magic Wand", required_gold=50, required_materials=30)