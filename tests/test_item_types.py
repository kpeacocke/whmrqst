import pytest

# Mock base Item class and subclasses for testing item types
class Item:
    def __init__(self, name, item_type):
        self.name = name
        self.item_type = item_type

class Weapon(Item):
    def __init__(self, name, attack_power):
        super().__init__(name, item_type="Weapon")
        self.attack_power = attack_power

class Armor(Item):
    def __init__(self, name, defense_rating):
        super().__init__(name, item_type="Armor")
        self.defense_rating = defense_rating

class Consumable(Item):
    def __init__(self, name, health_recovery):
        super().__init__(name, item_type="Consumable")
        self.health_recovery = health_recovery

class QuestItem(Item):
    def __init__(self, name):
        super().__init__(name, item_type="QuestItem")
        self.is_quest_item = True

# Test cases for Item Types

def test_weapon_initialization():
    # Scenario 1: Ensure weapons are correctly instantiated with attack power
    sword = Weapon(name="Sword", attack_power=10)
    
    assert sword.name == "Sword", "Weapon should have the name 'Sword'."
    assert sword.item_type == "Weapon", "Item type should be 'Weapon'."
    assert sword.attack_power == 10, "Sword attack power should be 10."

def test_armor_initialization():
    # Scenario 1: Ensure armor is correctly instantiated with defense rating
    shield = Armor(name="Shield", defense_rating=15)
    
    assert shield.name == "Shield", "Armor should have the name 'Shield'."
    assert shield.item_type == "Armor", "Item type should be 'Armor'."
    assert shield.defense_rating == 15, "Shield defense rating should be 15."

def test_consumable_initialization_and_usage():
    # Scenario 2: Ensure consumables are correctly instantiated and can be used
    potion = Consumable(name="Health Potion", health_recovery=20)
    
    assert potion.name == "Health Potion", "Consumable should be named 'Health Potion'."
    assert potion.item_type == "Consumable", "Item type should be 'Consumable'."
    assert potion.health_recovery == 20, "Health Potion should recover 20 health."

def test_quest_item_initialization():
    # Scenario 3: Ensure quest items are correctly instantiated and marked as quest items
    relic = QuestItem(name="Ancient Relic")
    
    assert relic.name == "Ancient Relic", "Quest item should have the name 'Ancient Relic'."
    assert relic.item_type == "QuestItem", "Item type should be 'QuestItem'."
    assert relic.is_quest_item, "Quest item should be marked as a quest item."

def test_item_attributes():
    # Scenario 4: Ensure items have correct attributes specific to their type
    sword = Weapon(name="Sword", attack_power=10)
    shield = Armor(name="Shield", defense_rating=15)
    potion = Consumable(name="Health Potion", health_recovery=20)
    
    assert sword.attack_power == 10, "Weapon should have correct attack power."
    assert shield.defense_rating == 15, "Armor should have correct defense rating."
    assert potion.health_recovery == 20, "Consumable should have correct health recovery."

def test_item_interactions():
    # Scenario 2: Ensure items interact correctly within game mechanics
    player_health = 50
    potion = Consumable(name="Health Potion", health_recovery=20)
    
    player_health += potion.health_recovery  # Simulate using the potion
    
    assert player_health == 70, "Player health should increase by 20 after using a health potion."