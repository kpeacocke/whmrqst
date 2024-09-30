import pytest

# Mock classes for Player, Item, and Encumbrance

class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

class Player:
    def __init__(self, strength):
        self.strength = strength
        self.items = []
        self.total_weight = 0
        self.base_carrying_capacity = 50  # Base carrying capacity without strength adjustments
        self.speed = 100  # Default speed

    def carrying_capacity(self):
        """Calculate the player's carrying capacity based on strength."""
        return self.base_carrying_capacity + (self.strength * 5)

    def add_item(self, item):
        """Add an item to the player's inventory and update weight."""
        self.items.append(item)
        self.total_weight += item.weight
        self.apply_encumbrance_penalty()

    def remove_item(self, item):
        """Remove an item from the player's inventory and update weight."""
        if item in self.items:
            self.items.remove(item)
            self.total_weight -= item.weight
        self.apply_encumbrance_penalty()

    def apply_encumbrance_penalty(self):
        """Apply penalties if the player is encumbered based on weight."""
        if self.total_weight > self.carrying_capacity():
            # Encumbered: reduce speed
            self.speed = 50  # Encumbered speed
        else:
            # Not encumbered: normal speed
            self.speed = 100

    def is_encumbered(self):
        """Check if the player is encumbered."""
        return self.total_weight > self.carrying_capacity()

# Test cases for Weight and Encumbrance

def test_add_item_weight_update():
    # Scenario 1: Ensure that weight is correctly calculated when items are added
    player = Player(strength=10)  # Strength affects carrying capacity
    item1 = Item(name="Sword", weight=10)
    item2 = Item(name="Shield", weight=15)

    player.add_item(item1)
    assert player.total_weight == 10, "Player's total weight should be updated to 10 after adding the sword."

    player.add_item(item2)
    assert player.total_weight == 25, "Player's total weight should be updated to 25 after adding the shield."

def test_remove_item_weight_update():
    # Scenario 1: Ensure that weight is correctly calculated when items are removed
    player = Player(strength=10)
    item1 = Item(name="Sword", weight=10)
    item2 = Item(name="Shield", weight=15)

    player.add_item(item1)
    player.add_item(item2)
    
    player.remove_item(item1)
    assert player.total_weight == 15, "Player's total weight should be updated to 15 after removing the sword."

def test_encumbrance_penalty():
    # Scenario 3: Ensure that encumbrance penalties are applied when the weight exceeds carrying capacity
    player = Player(strength=5)  # Strength gives limited carrying capacity
    item1 = Item(name="Heavy Armor", weight=40)
    item2 = Item(name="Greatsword", weight=30)

    player.add_item(item1)
    assert player.is_encumbered() == False, "Player should not be encumbered after adding only the armor."

    player.add_item(item2)
    assert player.is_encumbered(), "Player should be encumbered after adding the greatsword."
    assert player.speed == 50, "Player's speed should be reduced when encumbered."

def test_strength_increases_capacity():
    # Scenario 4: Ensure that strength increases the player's carrying capacity
    weak_player = Player(strength=5)  # Low strength
    strong_player = Player(strength=15)  # High strength

    assert weak_player.carrying_capacity() == 75, "Weak player should have a lower carrying capacity."
    assert strong_player.carrying_capacity() == 125, "Strong player should have a higher carrying capacity."

def test_varying_item_weights():
    # Scenario 5: Ensure that varying item weights are correctly accounted for
    player = Player(strength=10)
    light_item = Item(name="Dagger", weight=2)
    heavy_item = Item(name="Battle Axe", weight=25)

    player.add_item(light_item)
    player.add_item(heavy_item)

    assert player.total_weight == 27, "Player's total weight should be the sum of all item weights (27)."
    assert not player.is_encumbered(), "Player should not be encumbered with this total weight."

def test_encumbrance_boundary():
    # Scenario 2: Ensure that the player is encumbered when they carry exactly at capacity
    player = Player(strength=5)  # Carrying capacity should be 75 (50 + 25)

    item1 = Item(name="Heavy Armor", weight=50)
    item2 = Item(name="Helmet", weight=25)

    player.add_item(item1)
    player.add_item(item2)

    assert player.total_weight == 75, "Player's total weight should be 75."
    assert not player.is_encumbered(), "Player should not be encumbered when exactly at carrying capacity."

    # Add a small item to exceed capacity
    small_item = Item(name="Ring", weight=1)
    player.add_item(small_item)
    
    assert player.total_weight == 76, "Player's total weight should be 76 after adding the ring."
    assert player.is_encumbered(), "Player should be encumbered after exceeding the carrying capacity."