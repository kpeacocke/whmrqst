import pytest

# Mock classes for Core Systems

class Player:
    def __init__(self, health, inventory_capacity):
        self.health = health
        self.inventory = []
        self.inventory_capacity = inventory_capacity
        self.position = [0, 0]  # Simple [x, y] coordinate for player movement

    def move(self, dx, dy):
        """Move the player by dx, dy."""
        self.position[0] += dx
        self.position[1] += dy

    def pick_up_item(self, item):
        """Pick up an item if there's enough space in inventory."""
        if len(self.inventory) < self.inventory_capacity:
            self.inventory.append(item)
            return True
        return False

    def drop_item(self, item):
        """Drop an item from inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def take_damage(self, damage):
        """Reduce player's health by damage."""
        self.health -= damage

    def is_alive(self):
        """Check if the player is still alive."""
        return self.health > 0


class Enemy:
    def __init__(self, health, damage):
        self.health = health
        self.damage = damage

    def attack(self, player):
        """Attack the player and deal damage."""
        player.take_damage(self.damage)

    def take_damage(self, damage):
        """Reduce enemy's health by damage."""
        self.health -= damage

    def is_alive(self):
        """Check if the enemy is still alive."""
        return self.health > 0


class WorldObject:
    def __init__(self, name, interactable):
        self.name = name
        self.interactable = interactable

    def interact(self, player):
        """Simulate player interaction with the object."""
        if self.interactable:
            return f"Player interacts with {self.name}"
        return f"{self.name} is not interactable."


# Test cases for Phase 1 Core Systems

# Player Movement System

def test_player_movement():
    # Ensure the player can move correctly
    player = Player(health=100, inventory_capacity=5)
    
    player.move(5, 3)
    assert player.position == [5, 3], "Player should move to position [5, 3]."
    
    player.move(-2, 1)
    assert player.position == [3, 4], "Player should move to position [3, 4] after second move."

# Inventory System

def test_inventory_pick_up_item():
    # Ensure the player can pick up items if there's space
    player = Player(health=100, inventory_capacity=3)
    
    assert player.pick_up_item("Sword"), "Player should be able to pick up the sword."
    assert player.pick_up_item("Shield"), "Player should be able to pick up the shield."
    assert player.pick_up_item("Potion"), "Player should be able to pick up the potion."
    
    assert len(player.inventory) == 3, "Inventory should contain three items."
    
    # Inventory is full now
    assert not player.pick_up_item("Helmet"), "Player should not be able to pick up an item if inventory is full."

def test_inventory_drop_item():
    # Ensure the player can drop items from their inventory
    player = Player(health=100, inventory_capacity=3)
    player.pick_up_item("Sword")
    player.pick_up_item("Shield")
    
    assert player.drop_item("Sword"), "Player should be able to drop the sword."
    assert "Sword" not in player.inventory, "Sword should be removed from inventory."
    
    assert player.drop_item("Shield"), "Player should be able to drop the shield."
    assert "Shield" not in player.inventory, "Shield should be removed from inventory."

# Basic Combat System

def test_combat_player_takes_damage():
    # Ensure the player takes damage correctly
    player = Player(health=100, inventory_capacity=5)
    enemy = Enemy(health=50, damage=20)
    
    enemy.attack(player)
    assert player.health == 80, "Player should take 20 damage, health should be 80."

def test_combat_enemy_takes_damage():
    # Ensure the enemy takes damage correctly
    enemy = Enemy(health=50, damage=20)
    
    enemy.take_damage(30)
    assert enemy.health == 20, "Enemy should take 30 damage, health should be 20."

    assert enemy.is_alive(), "Enemy should still be alive."
    
    enemy.take_damage(20)
    assert not enemy.is_alive(), "Enemy should be dead after taking 20 more damage."

# Interaction with World Objects

def test_interact_with_world_object():
    # Ensure the player can interact with objects in the world
    chest = WorldObject(name="Chest", interactable=True)
    wall = WorldObject(name="Wall", interactable=False)
    
    assert chest.interact(None) == "Player interacts with Chest", "Player should interact with the chest."
    assert wall.interact(None) == "Wall is not interactable.", "Player should not be able to interact with the wall."