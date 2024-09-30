import pytest

# Mock Character class for death and injury mechanics
class Character:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        self.is_dead = False
        self.injuries = {"strength": 0, "agility": 0, "intelligence": 0}  # Injury penalties

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_dead = True

    def apply_injury(self, attribute, penalty):
        if attribute in self.injuries:
            self.injuries[attribute] += penalty

    def heal_injury(self, attribute, amount):
        if attribute in self.injuries and self.injuries[attribute] > 0:
            self.injuries[attribute] -= amount
            if self.injuries[attribute] < 0:
                self.injuries[attribute] = 0

    def revive(self):
        if self.is_dead:
            self.is_dead = False
            self.health = 50  # Revived with half health, for example

# Test cases for Death and Injury

def test_character_death():
    # Scenario 1: Ensure character dies when health reaches zero
    char = Character(name="Hero", health=50)
    char.take_damage(60)
    
    assert char.is_dead, "Character should be marked as dead when health reaches 0."
    assert char.health == 0, "Character's health should not drop below 0."

def test_injury_penalty():
    # Scenario 2: Ensure injuries apply penalties to attributes
    char = Character(name="Hero", health=100)
    
    # Apply an injury to strength, decreasing it by 3 points
    char.apply_injury("strength", 3)
    
    assert char.injuries["strength"] == 3, "Strength injury penalty should be 3."

def test_recover_from_injury():
    # Scenario 3: Ensure character can recover from injuries
    char = Character(name="Hero", health=100)
    
    # Apply and then heal an injury to strength
    char.apply_injury("strength", 5)
    char.heal_injury("strength", 2)
    
    assert char.injuries["strength"] == 3, "Strength penalty should be reduced to 3 after healing."

def test_death_revival():
    # Scenario 4: Ensure character can be revived after death
    char = Character(name="Hero", health=100)
    
    # Character takes enough damage to die
    char.take_damage(150)
    assert char.is_dead, "Character should be dead after taking fatal damage."
    
    # Revive the character
    char.revive()
    
    assert not char.is_dead, "Character should no longer be dead after revival."
    assert char.health == 50, "Character should be revived with 50 health."

def test_health_cannot_drop_below_zero():
    # Scenario 5: Ensure health cannot drop below zero
    char = Character(name="Hero", health=50)
    char.take_damage(100)  # Deal more damage than character's health
    
    assert char.health == 0, "Character's health should be 0 and not go below zero."
    assert char.is_dead, "Character should be dead if health is 0."