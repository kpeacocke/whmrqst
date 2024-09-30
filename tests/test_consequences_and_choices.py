import pytest

# Mock Character class for testing purposes
class Character:
    def __init__(self, name, health=100, reputation=0):
        self.name = name
        self.health = health
        self.reputation = reputation

    def modify_health(self, amount):
        self.health += amount
        if self.health < 0:
            self.health = 0
        elif self.health > 100:
            self.health = 100

    def modify_reputation(self, amount):
        self.reputation += amount

# Mock Choice system for testing purposes
class Choice:
    def __init__(self, description, consequence_func):
        self.description = description
        self.consequence_func = consequence_func  # Function to call for consequences

    def apply_consequence(self, character):
        self.consequence_func(character)

# Test cases for Consequences and Choices

def test_choice_alters_health():
    # Scenario 1: A choice that alters character's health
    char = Character(name="Hero", health=50)
    
    # Choice to heal the character
    heal_choice = Choice(
        description="Drink a healing potion.",
        consequence_func=lambda character: character.modify_health(20)
    )
    
    # Apply the consequence
    heal_choice.apply_consequence(char)

    assert char.health == 70, "Character's health should increase by 20, making it 70."

def test_choice_affects_reputation():
    # Scenario 2: A choice that affects reputation
    char = Character(name="Hero", reputation=0)
    
    # Choice to help an NPC, increases reputation
    help_npc_choice = Choice(
        description="Help the villager.",
        consequence_func=lambda character: character.modify_reputation(10)
    )
    
    # Apply the consequence
    help_npc_choice.apply_consequence(char)

    assert char.reputation == 10, "Character's reputation should increase by 10."

def test_negative_consequence():
    # Scenario 3: A choice that leads to a negative consequence (health reduction)
    char = Character(name="Hero", health=80)
    
    # Choice to enter a dangerous area, reduces health
    dangerous_choice = Choice(
        description="Enter the dangerous forest.",
        consequence_func=lambda character: character.modify_health(-30)
    )
    
    # Apply the consequence
    dangerous_choice.apply_consequence(char)

    assert char.health == 50, "Character's health should decrease by 30, making it 50."

def test_long_term_consequence():
    # Scenario 4: A long-term consequence based on a previous choice
    char = Character(name="Hero", reputation=0)
    
    # Choice to betray an NPC, reducing reputation in the long term
    betray_choice = Choice(
        description="Betray the NPC.",
        consequence_func=lambda character: character.modify_reputation(-20)
    )
    
    # Apply the consequence of betrayal
    betray_choice.apply_consequence(char)

    # Simulate a later consequence: reduced help from villagers
    assert char.reputation == -20, "Character's reputation should decrease by 20 after betrayal."

    # Suppose the long-term consequence is NPCs refusing help if reputation is too low
    def long_term_event(character):
        if character.reputation < -10:
            return "Villagers refuse to help you."
        else:
            return "Villagers welcome you."

    event_result = long_term_event(char)
    assert event_result == "Villagers refuse to help you.", "Villagers should refuse to help due to low reputation."