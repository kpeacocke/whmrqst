import pytest

# Mock Item class for inventory management
class Item:
    def __init__(self, name, value):
        self.name = name
        self.value = value

# Mock Character class for core feature testing
class Character:
    def __init__(self, name, level=1, xp=0, inventory=None):
        self.name = name
        self.level = level
        self.xp = xp
        self.inventory = inventory if inventory else []
        self.attributes = {"strength": 10, "agility": 10, "intelligence": 10}

    def gain_xp(self, amount):
        self.xp += amount
        # Simulate leveling up when XP threshold is reached
        while self.xp >= 100:
            self.xp -= 100
            self.level_up()

    def level_up(self):
        self.level += 1
        self.attributes["strength"] += 2
        self.attributes["agility"] += 2
        self.attributes["intelligence"] += 2

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item_name):
        self.inventory = [item for item in self.inventory if item.name != item_name]

    def move(self, direction):
        # Simulate simple movement logic
        return f"Moved {direction}"

# Test cases for Core Features

def test_character_creation():
    # Scenario 1: Ensure character creation initializes attributes and inventory correctly
    char = Character(name="Hero")
    assert char.name == "Hero", "Character name should be 'Hero'"
    assert char.level == 1, "Character should start at level 1"
    assert char.xp == 0, "Character should start with 0 XP"
    assert len(char.inventory) == 0, "Character inventory should be empty on creation"
    assert char.attributes["strength"] == 10, "Character should start with 10 strength"
    assert char.attributes["agility"] == 10, "Character should start with 10 agility"
    assert char.attributes["intelligence"] == 10, "Character should start with 10 intelligence"

def test_character_leveling_up():
    # Scenario 2: Ensure character gains XP and levels up correctly
    char = Character(name="Hero", xp=90)
    char.gain_xp(20)  # Gain 20 XP (90 + 20 = 110 XP, should level up and leave 10 XP)
    
    assert char.level == 2, "Character should level up to level 2 after gaining 100 XP"
    assert char.xp == 10, "Character should have 10 XP remaining after leveling up"
    assert char.attributes["strength"] == 12, "Strength should increase by 2 upon leveling up"
    assert char.attributes["agility"] == 12, "Agility should increase by 2 upon leveling up"
    assert char.attributes["intelligence"] == 12, "Intelligence should increase by 2 upon leveling up"

def test_inventory_management():
    # Scenario 3: Ensure items are added/removed from inventory correctly
    char = Character(name="Hero")
    sword = Item(name="Sword", value=50)
    shield = Item(name="Shield", value=30)
    
    char.add_item(sword)
    char.add_item(shield)
    
    assert len(char.inventory) == 2, "Character should have 2 items in inventory"
    assert char.inventory[0].name == "Sword", "First item should be Sword"
    
    # Remove Sword from inventory
    char.remove_item("Sword")
    
    assert len(char.inventory) == 1, "Character should have 1 item in inventory after removal"
    assert char.inventory[0].name == "Shield", "Remaining item should be Shield"

def test_movement():
    # Scenario 4: Ensure character can move in different directions
    char = Character(name="Hero")
    
    result = char.move("north")
    assert result == "Moved north", "Character should move north"
    
    result = char.move("south")
    assert result == "Moved south", "Character should move south"