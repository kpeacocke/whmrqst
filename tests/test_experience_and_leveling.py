import pytest

# Mock Character class for experience and leveling
class Character:
    def __init__(self, name, level=1, xp=0, xp_to_next_level=100):
        self.name = name
        self.level = level
        self.xp = xp
        self.xp_to_next_level = xp_to_next_level
        self.attributes = {"strength": 10, "agility": 10, "intelligence": 10}
        self.max_level = 10

    def gain_xp(self, amount):
        """Character gains experience points, leveling up if they reach the XP threshold."""
        self.xp += amount
        while self.xp >= self.xp_to_next_level and self.level < self.max_level:
            self.xp -= self.xp_to_next_level
            self.level_up()

    def level_up(self):
        """Level up the character, increase attributes."""
        self.level += 1
        self.attributes["strength"] += 2
        self.attributes["agility"] += 2
        self.attributes["intelligence"] += 2
        # Increase XP required for next level
        self.xp_to_next_level += 50

    def set_max_level(self, level):
        self.max_level = level

# Test cases for Experience and Leveling

def test_gain_xp_and_level_up():
    # Scenario 1: Ensure gaining XP works and characters level up when reaching XP threshold
    char = Character(name="Hero", xp=90)
    char.gain_xp(20)  # Gain 20 XP (90 + 20 = 110, should level up and leave 10 XP)
    
    assert char.level == 2, "Character should level up to level 2 after gaining 100 XP."
    assert char.xp == 10, "Character should have 10 XP remaining after leveling up."
    assert char.xp_to_next_level == 150, "XP required for next level should increase after leveling up."

def test_attributes_increase_on_level_up():
    # Scenario 2: Ensure that character's attributes increase upon leveling up
    char = Character(name="Hero", xp=90)
    char.gain_xp(20)  # Gain XP and level up
    
    assert char.level == 2, "Character should level up to level 2."
    assert char.attributes["strength"] == 12, "Strength should increase by 2 after leveling up."
    assert char.attributes["agility"] == 12, "Agility should increase by 2 after leveling up."
    assert char.attributes["intelligence"] == 12, "Intelligence should increase by 2 after leveling up."

def test_excess_xp_carryover():
    # Scenario 3: Ensure that excess XP carries over after leveling up
    char = Character(name="Hero", xp=90)
    char.gain_xp(110)  # Gain 110 XP, enough to level up once and leave excess XP (90 + 110 = 200)
    
    assert char.level == 3, "Character should level up twice to level 3."
    assert char.xp == 50, "Character should have 50 XP remaining after leveling up twice."
    assert char.xp_to_next_level == 200, "XP required for next level should increase accordingly."

def test_level_cap():
    # Scenario 4: Ensure that characters cannot exceed the maximum level
    char = Character(name="Hero", xp=90)
    char.set_max_level(5)  # Set maximum level to 5
    
    # Gain enough XP to potentially level up past the cap
    char.gain_xp(1000)
    
    assert char.level == 5, "Character should not exceed level 5."
    assert char.xp == 0, "Character should not have any XP after reaching max level."
    assert char.xp_to_next_level == 300, "XP to next level should not matter after reaching max level."