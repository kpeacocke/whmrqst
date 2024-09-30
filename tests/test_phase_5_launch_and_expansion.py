import pytest
import json

# Mock classes for Game State, Save/Load, and Expansion

class GameState:
    def __init__(self, player_health, inventory, quest_status):
        self.player_health = player_health
        self.inventory = inventory
        self.quest_status = quest_status

    def save_game(self):
        """Serialize game state to a string (simulating saving to a file)."""
        return json.dumps({
            'player_health': self.player_health,
            'inventory': [item.name for item in self.inventory.items],
            'quest_status': self.quest_status
        })

    @staticmethod
    def load_game(saved_data):
        """Deserialize game state from a string (simulating loading from a file)."""
        data = json.loads(saved_data)
        game_state = GameState(
            player_health=data['player_health'],
            inventory=Inventory(capacity=10),
            quest_status=data['quest_status']
        )
        for item_name in data['inventory']:
            game_state.inventory.add_item(Item(name=item_name))
        return game_state


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                return True
        return False


class Item:
    def __init__(self, name):
        self.name = name


class ExpansionContent:
    def __init__(self):
        self.new_quests = []
        self.new_items = []

    def add_new_quest(self, quest_name):
        """Add new quest from expansion content."""
        self.new_quests.append(quest_name)

    def add_new_item(self, item_name):
        """Add new item from expansion content."""
        self.new_items.append(Item(name=item_name))

    def integrate_into_game(self, game_state):
        """Integrate new quests and items into the existing game state."""
        for quest in self.new_quests:
            game_state.quest_status[quest] = 'Not Started'
        for item in self.new_items:
            game_state.inventory.add_item(item)


# Test cases for Phase 5 Launch and Expansion

# Game State Persistence

def test_save_and_load_game_state():
    # Ensure the game state can be saved and loaded correctly
    inventory = Inventory(capacity=5)
    sword = Item(name="Sword")
    shield = Item(name="Shield")
    inventory.add_item(sword)
    inventory.add_item(shield)

    quest_status = {"Main Quest": "In Progress"}
    
    # Create game state and save it
    game_state = GameState(player_health=100, inventory=inventory, quest_status=quest_status)
    saved_data = game_state.save_game()

    # Load game state from saved data
    loaded_game_state = GameState.load_game(saved_data)
    
    assert loaded_game_state.player_health == 100, "Player health should be restored to 100."
    assert len(loaded_game_state.inventory.items) == 2, "Inventory should have two items after loading."
    assert loaded_game_state.quest_status["Main Quest"] == "In Progress", "Quest status should be restored after loading."

def test_save_and_load_empty_game_state():
    # Ensure empty game state can be saved and loaded
    inventory = Inventory(capacity=5)
    quest_status = {}

    # Create an empty game state
    game_state = GameState(player_health=100, inventory=inventory, quest_status=quest_status)
    saved_data = game_state.save_game()

    # Load game state from saved data
    loaded_game_state = GameState.load_game(saved_data)
    
    assert loaded_game_state.player_health == 100, "Player health should be restored."
    assert len(loaded_game_state.inventory.items) == 0, "Inventory should be empty after loading."
    assert loaded_game_state.quest_status == {}, "Quest status should be empty after loading."

# Expansion Content Integration

def test_integrate_expansion_content():
    # Ensure that new expansion content can be integrated into the game
    inventory = Inventory(capacity=5)
    quest_status = {"Main Quest": "In Progress"}
    
    # Create initial game state
    game_state = GameState(player_health=100, inventory=inventory, quest_status=quest_status)

    # Create expansion content
    expansion = ExpansionContent()
    expansion.add_new_quest("Find the Hidden Gem")
    expansion.add_new_item("Mystic Amulet")

    # Integrate expansion content into game state
    expansion.integrate_into_game(game_state)

    assert "Find the Hidden Gem" in game_state.quest_status, "New quest should be integrated into the game state."
    assert len(game_state.inventory.items) == 1, "New item should be added to the inventory."

# Stress Testing

def test_large_inventory_save_and_load():
    # Ensure game state can handle saving and loading a large inventory
    inventory = Inventory(capacity=1000)
    for i in range(1000):
        inventory.add_item(Item(name=f"Item_{i}"))
    
    quest_status = {"Main Quest": "In Progress"}
    
    # Create game state and save it
    game_state = GameState(player_health=100, inventory=inventory, quest_status=quest_status)
    saved_data = game_state.save_game()

    # Load game state from saved data
    loaded_game_state = GameState.load_game(saved_data)
    
    assert len(loaded_game_state.inventory.items) == 1000, "Inventory should contain 1000 items after loading."
    assert loaded_game_state.quest_status["Main Quest"] == "In Progress", "Quest status should be restored after loading."