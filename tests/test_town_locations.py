import pytest

# Mock classes for Town and Player

class Town:
    def __init__(self, name, x, y, features=None):
        """Initialize a town with a name, coordinates, and optional features (e.g., shops, NPCs)."""
        self.name = name
        self.x = x  # x-coordinate
        self.y = y  # y-coordinate
        self.features = features or []

    def has_feature(self, feature):
        """Check if the town has a specific feature (e.g., shop, NPC)."""
        return feature in self.features

    def distance_to(self, other_town):
        """Calculate the distance to another town (e.g., Euclidean distance)."""
        return ((self.x - other_town.x) ** 2 + (self.y - other_town.y) ** 2) ** 0.5

class Player:
    def __init__(self, current_town):
        self.current_town = current_town

    def travel_to(self, new_town):
        """Travel to a new town."""
        self.current_town = new_town


# Test cases for Town Locations

def test_town_initialization():
    # Scenario 1: Ensure that towns are correctly initialized
    town = Town(name="Eldoria", x=100, y=200, features=["shop", "inn"])
    assert town.name == "Eldoria", "Town should be initialized with the correct name."
    assert town.x == 100 and town.y == 200, "Town should have correct geographical coordinates."
    assert town.has_feature("shop"), "Town should have a shop as a feature."
    assert town.has_feature("inn"), "Town should have an inn as a feature."

def test_town_travel():
    # Scenario 2: Ensure players can travel between towns
    town1 = Town(name="Eldoria", x=100, y=200)
    town2 = Town(name="Dunharrow", x=300, y=400)
    
    player = Player(current_town=town1)
    assert player.current_town == town1, "Player should start in Eldoria."
    
    player.travel_to(town2)
    assert player.current_town == town2, "Player should now be in Dunharrow after traveling."

def test_town_features():
    # Scenario 3: Ensure town-specific features are accessible
    town = Town(name="Eldoria", x=100, y=200, features=["blacksmith", "tavern", "market"])
    
    assert town.has_feature("blacksmith"), "Town should have a blacksmith."
    assert town.has_feature("tavern"), "Town should have a tavern."
    assert town.has_feature("market"), "Town should have a market."
    assert not town.has_feature("library"), "Town should not have a library."

def test_town_interaction():
    # Scenario 4: Ensure that town interactions (e.g., visiting shops) work as expected
    town = Town(name="Eldoria", x=100, y=200, features=["shop", "inn"])
    
    assert town.has_feature("shop"), "Player should be able to visit the shop in Eldoria."
    assert town.has_feature("inn"), "Player should be able to rest at the inn in Eldoria."

def test_town_distance_calculation():
    # Scenario 5: Ensure that distance calculations between towns work correctly
    town1 = Town(name="Eldoria", x=100, y=200)
    town2 = Town(name="Dunharrow", x=400, y=800)
    
    distance = town1.distance_to(town2)
    expected_distance = ((100 - 400) ** 2 + (200 - 800) ** 2) ** 0.5
    assert distance == expected_distance, "Distance calculation between towns should be correct."