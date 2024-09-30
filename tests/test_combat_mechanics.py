import pytest
import random

# Mock Character class for testing purposes
class Character:
    def __init__(self, name, strength, defense, hp, crit_chance=0):
        self.name = name
        self.strength = strength
        self.defense = defense
        self.hp = hp
        self.crit_chance = crit_chance

    def is_critical_hit(self):
        # Simulate a critical hit based on the character's critical chance
        return random.random() < self.crit_chance

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0


# Mock Combat class for testing purposes
class Combat:
    def __init__(self):
        # The Combat class currently does not require any initialization parameters.
        pass

    def attack(self, attacker, defender):
        # Attack success is determined by comparing the attacker's strength and defender's defense
        attack_roll = random.randint(1, 20) + attacker.strength
        if attack_roll > defender.defense:
            # If critical hit, deal double damage
            if attacker.is_critical_hit():
                return self.calculate_damage(attacker) * 2
            return self.calculate_damage(attacker)
        else:
            return 0  # Attack missed

    def calculate_damage(self, attacker):
        # Simple damage calculation: strength + random modifier
        return attacker.strength + random.randint(1, 6)


# Test cases for Combat Mechanics

def test_attack_success():
    # Scenario 1: Ensure that an attack succeeds or fails based on strength vs defense
    attacker = Character(name="Warrior", strength=10, defense=0, hp=100)
    defender = Character(name="Orc", strength=5, defense=12, hp=100)

    combat = Combat()

    # Test with fixed roll to ensure reproducibility (mocking random.randint to simulate different outcomes)
    random.seed(1)  # Seed random for reproducible results

    damage = combat.attack(attacker, defender)
    if damage > 0:
        assert defender.hp == 100 - damage, f"Defender HP should decrease by {damage}, but got {defender.hp}"
    else:
        assert defender.hp == 100, "Defender HP should remain 100 if attack misses"

def test_damage_calculation():
    # Scenario 2: Ensure that damage is correctly calculated based on strength
    attacker = Character(name="Warrior", strength=8, defense=0, hp=100)
    defender = Character(name="Orc", strength=5, defense=10, hp=50)

    combat = Combat()

    # Mocking a successful attack and checking damage
    random.seed(1)  # Seed for reproducibility
    damage = combat.attack(attacker, defender)

    assert defender.hp == 50 - damage, f"Defender HP should decrease by {damage}, but got {defender.hp}"
    assert 9 <= damage <= 14, f"Damage should be between 9 and 14 (strength + random 1-6), but got {damage}"

def test_critical_hit():
    # Scenario 3: Ensure critical hits deal double damage
    attacker = Character(name="Assassin", strength=10, defense=0, hp=100, crit_chance=1.0)  # Guaranteed crit
    defender = Character(name="Orc", strength=5, defense=10, hp=50)

    combat = Combat()

    random.seed(1)  # Seed random for reproducible results
    damage = combat.attack(attacker, defender)

    assert damage >= 20, f"Critical hit should deal at least 20 damage, but got {damage}."
    assert defender.hp == 50 - damage, f"Defender HP should decrease by {damage}, but got {defender.hp}"