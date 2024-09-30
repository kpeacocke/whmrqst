import pytest

# Mock Character class with attributes for testing
class Character:
    def __init__(self, strength=10, agility=10, intelligence=10):
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.hp = self.calculate_hp()

    def calculate_hp(self):
        # HP could be based on strength; adjust logic as needed
        return 10 + self.strength * 2

    def modify_attribute(self, attribute_name, modifier):
        if hasattr(self, attribute_name):
            setattr(self, attribute_name, getattr(self, attribute_name) + modifier)
            if attribute_name == "strength":
                # Recalculate HP if strength changes
                self.hp = self.calculate_hp()

# Test cases for Attributes

def test_attributes_initialization():
    # Scenario 1: Ensure that attributes are initialized correctly
    char = Character(strength=15, agility=12, intelligence=8)
    assert char.strength == 15, "Strength should be initialized to 15"
    assert char.agility == 12, "Agility should be initialized to 12"
    assert char.intelligence == 8, "Intelligence should be initialized to 8"
    assert char.hp == 40, "HP should be calculated based on strength"

def test_modify_attributes():
    # Scenario 2: Ensure that attributes can be modified
    char = Character(strength=10)
    char.modify_attribute("strength", 5)
    assert char.strength == 15, "Strength should be modified to 15"
    assert char.hp == 40, "HP should be recalculated when strength is modified"

    char.modify_attribute("agility", -3)
    assert char.agility == 7, "Agility should be decreased by 3"

def test_derived_attributes():
    # Scenario 3: Ensure that derived attributes (like HP) are calculated correctly
    char = Character(strength=20)
    assert char.hp == 50, "HP should be derived from strength (20 * 2 + 10)"
    
    # Test again after modifying strength
    char.modify_attribute("strength", -10)
    assert char.hp == 30, "HP should be recalculated after modifying strength"