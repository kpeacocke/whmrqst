import pytest

# Mock Character class for testing purposes
class Character:
    def __init__(self, name, class_type, race):
        self.name = name
        self.class_type = class_type
        self.race = race
        self.strength = self.calculate_strength()
        self.agility = self.calculate_agility()
        self.intelligence = self.calculate_intelligence()
        self.equipment = self.get_initial_equipment()

    def calculate_strength(self):
        # Calculate strength based on class and race
        base_strength = 10
        class_strength_bonus = {
            "Warrior": 5,
            "Thief": 0,
            "Wizard": 0
        }
        race_strength_bonus = {
            "Dwarf": 3,
            "Elf": 0,
            "Human": 0
        }
        return base_strength + class_strength_bonus.get(self.class_type, 0) + race_strength_bonus.get(self.race, 0)

    def calculate_agility(self):
        # Calculate agility based on class and race
        base_agility = 10
        class_agility_bonus = {
            "Warrior": 0,
            "Thief": 5,
            "Wizard": 0
        }
        race_agility_bonus = {
            "Dwarf": 0,
            "Elf": 3,
            "Human": 0
        }
        return base_agility + class_agility_bonus.get(self.class_type, 0) + race_agility_bonus.get(self.race, 0)

    def calculate_intelligence(self):
        # Calculate intelligence based on class and race
        base_intelligence = 10
        class_intelligence_bonus = {
            "Warrior": 0,
            "Thief": 0,
            "Wizard": 5
        }
        race_intelligence_bonus = {
            "Dwarf": 0,
            "Elf": 0,
            "Human": 2
        }
        return base_intelligence + class_intelligence_bonus.get(self.class_type, 0) + race_intelligence_bonus.get(self.race, 0)

    def get_initial_equipment(self):
        # Equipment based on class
        equipment_by_class = {
            "Warrior": ["sword", "shield"],
            "Wizard": ["staff", "spellbook"],
            "Thief": ["dagger", "lockpick"]
        }
        return equipment_by_class.get(self.class_type, ["basic equipment"])


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
    assert char.name == "Gandalf", "Character name should be 'Gandalf'"
    assert char.class_type == "Wizard", "Character class should be 'Wizard'"
    assert char.race == "Human", "Character race should be 'Human'"
    assert char.strength == 10, "Wizard's default strength should be 10"
    assert char.agility == 10, "Wizard's default agility should be 10"
    assert char.intelligence == 15, "Wizard's default intelligence should be 15 (base 10 + 5)"
    assert char.equipment == ["staff", "spellbook"], "Wizard should start with staff and spellbook"

def test_race_influences_attributes():
    # Scenario 3: Ensure race influences starting attributes
    dwarf_warrior = Character(name="Thorin", class_type="Warrior", race="Dwarf")
    elf_thief = Character(name="Legolas", class_type="Thief", race="Elf")
    
    # Dwarf Warrior
    assert dwarf_warrior.name == "Thorin", "Character name should be 'Thorin'"
    assert dwarf_warrior.class_type == "Warrior", "Character class should be 'Warrior'"
    assert dwarf_warrior.race == "Dwarf", "Character race should be 'Dwarf'"
    assert dwarf_warrior.strength == 18, "Dwarf Warrior's strength should be 18 (base 10 + 5 from Warrior + 3 from Dwarf)"
    assert dwarf_warrior.agility == 10, "Dwarf Warrior's agility should be 10"
    assert dwarf_warrior.intelligence == 10, "Dwarf Warrior's intelligence should be 10"
    
    # Elf Thief
    assert elf_thief.name == "Legolas", "Character name should be 'Legolas'"
    assert elf_thief.class_type == "Thief", "Character class should be 'Thief'"
    assert elf_thief.race == "Elf", "Character race should be 'Elf'"
    assert elf_thief.strength == 10, "Elf Thief's strength should be 10"
    assert elf_thief.agility == 18, "Elf Thief's agility should be 18 (base 10 + 5 from Thief + 3 from Elf)"
    assert elf_thief.intelligence == 10, "Elf Thief's intelligence should be 10"
    assert elf_thief.equipment == ["dagger", "lockpick"], "Thief should start with dagger and lockpick"