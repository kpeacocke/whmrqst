import pytest

# Mock Character class for testing purposes
class Character:
    def __init__(self, name, class_type, race):
        self.name = name
        self.class_type = class_type
        self.race = race
        self.strength = self.get_initial_strength()
        self.agility = self.get_initial_agility()
        self.intelligence = self.get_initial_intelligence()
        self.equipment = self.get_initial_equipment()

    def get_initial_strength(self):
        # Strength based on class and race
        base_strength = 10
        if self.class_type == "Warrior":
            base_strength += 5
        if self.race == "Dwarf":
            base_strength += 3
        return base_strength

    def get_initial_agility(self):
        # Agility based on class and race
        base_agility = 10
        if self.class_type == "Thief":
            base_agility += 5
        if self.race == "Elf":
            base_agility += 3
        return base_agility

    def get_initial_intelligence(self):
        # Intelligence based on class and race
        base_intelligence = 10
        if self.class_type == "Wizard":
            base_intelligence += 5
        if self.race == "Human":
            base_intelligence += 2
        return base_intelligence

    def get_initial_equipment(self):
        # Equipment based on class
        if self.class_type == "Warrior":
            return ["sword", "shield"]
        elif self.class_type == "Wizard":
            return ["staff", "spellbook"]
        elif self.class_type == "Thief":
            return ["dagger", "lockpick"]
        return ["basic equipment"]


# Test cases for Character Creation

def test_default_character_creation():
    # Scenario 1: Ensure a character is created with default attributes
    char = Character(name="Hero", class_type="Warrior", race="Human")
    assert char.name == "Hero", "Character name should be 'Hero'"
    assert char.class_type == "Warrior", "Character class should be 'Warrior'"
    assert char.race == "Human", "Character race should be 'Human'"
    assert char.strength == 15, "Warrior's default strength should be 15 (base 10 + 5)"
    assert char.agility == 10, "Warrior's default agility should be 10"
    assert char.intelligence == 12, "Human's intelligence should be 12 (base 10 + 2)"
    assert char.equipment == ["sword", "shield"], "Warrior should start with sword and shield"

def test_wizard_character_creation():
    # Scenario 2: Ensure a Wizard starts with correct attributes and equipment
    char = Character(name="Gandalf", class_type="Wizard", race="Human")
    assert char.strength == 10, "Wizard's default strength should be 10"
    assert char.agility == 10, "Wizard's default agility should be 10"
    assert char.intelligence == 15, "Wizard's default intelligence should be 15 (base 10 + 5)"
    assert char.equipment == ["staff", "spellbook"], "Wizard should start with staff and spellbook"

def test_race_influences_attributes():
    # Scenario 3: Ensure race influences starting attributes
    dwarf_warrior = Character(name="Thorin", class_type="Warrior", race="Dwarf")
    elf_thief = Character(name="Legolas", class_type="Thief", race="Elf")
    
    # Dwarf Warrior
    assert dwarf_warrior.strength == 18, "Dwarf Warrior's strength should be 18 (base 10 + 5 from Warrior + 3 from Dwarf)"
    assert dwarf_warrior.agility == 10, "Dwarf Warrior's agility should be 10"
    
    # Elf Thief
    assert elf_thief.strength == 10, "Elf Thief's strength should be 10"
    assert elf_thief.agility == 18, "Elf Thief's agility should be 18 (base 10 + 5 from Thief + 3 from Elf)"
    assert elf_thief.equipment == ["dagger", "lockpick"], "Thief should start with dagger and lockpick"