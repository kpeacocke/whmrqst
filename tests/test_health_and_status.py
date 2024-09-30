import pytest

# Mock Character class for health and status mechanics
class Character:
    def __init__(self, name, health=100, max_health=100):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.status_effects = []  # List of status effects (e.g., "poisoned", "stunned")

    def take_damage(self, amount):
        """Reduce health when taking damage, but health cannot go below zero."""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        """Increase health when healing, but health cannot exceed max health."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def apply_status_effect(self, effect):
        """Apply a status effect if it's not already active."""
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def clear_status_effect(self, effect):
        """Remove a status effect."""
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def process_status_effects(self):
        """Process status effects like poison (e.g., reduce health over time)."""
        if "poisoned" in self.status_effects:
            self.take_damage(10)  # Poison reduces health by 10 each turn

# Test cases for Health and Status

def test_take_damage():
    # Scenario 1: Ensure health decreases when taking damage, but not below zero
    char = Character(name="Hero", health=50)
    char.take_damage(30)
    
    assert char.health == 20, "Health should decrease by 30 to 20."
    
    char.take_damage(50)
    assert char.health == 0, "Health should not drop below zero."

def test_healing():
    # Scenario 2: Ensure health increases when healing, but not above max health
    char = Character(name="Hero", health=50, max_health=100)
    char.heal(30)
    
    assert char.health == 80, "Health should increase by 30 to 80."
    
    char.heal(50)
    assert char.health == 100, "Health should not exceed max health of 100."

def test_apply_status_effect():
    # Scenario 3: Ensure status effects are applied correctly
    char = Character(name="Hero")
    
    char.apply_status_effect("poisoned")
    assert "poisoned" in char.status_effects, "Poisoned status should be applied."
    
    char.apply_status_effect("stunned")
    assert "stunned" in char.status_effects, "Stunned status should be applied."

def test_clear_status_effect():
    # Scenario 3: Ensure status effects can be cleared
    char = Character(name="Hero")
    
    char.apply_status_effect("poisoned")
    char.clear_status_effect("poisoned")
    
    assert "poisoned" not in char.status_effects, "Poisoned status should be cleared."

def test_process_poison_effect():
    # Scenario 4: Ensure poison status causes damage over time
    char = Character(name="Hero", health=50)
    
    # Apply poison and process the effect
    char.apply_status_effect("poisoned")
    char.process_status_effects()
    
    assert char.health == 40, "Poison should reduce health by 10 each turn."
    
    char.process_status_effects()
    assert char.health == 30, "Poison should continue to reduce health by 10 each turn."

def test_status_effects_persistence():
    # Ensure multiple status effects are handled and removed correctly
    char = Character(name="Hero")
    
    # Apply multiple status effects
    char.apply_status_effect("poisoned")
    char.apply_status_effect("stunned")
    
    assert "poisoned" in char.status_effects, "Poisoned status should be active."
    assert "stunned" in char.status_effects, "Stunned status should be active."
    
    # Clear the poisoned status
    char.clear_status_effect("poisoned")
    assert "poisoned" not in char.status_effects, "Poisoned status should be cleared."
    assert "stunned" in char.status_effects, "Stunned status should remain active."

def test_health_cannot_exceed_max_health():
    # Scenario: Ensure health cannot exceed maximum health when healing
    char = Character(name="Hero", health=90, max_health=100)
    
    char.heal(20)
    assert char.health == 100, "Health should not exceed max health even with healing."

def test_health_cannot_drop_below_zero():
    # Scenario: Ensure health cannot drop below zero when taking excessive damage
    char = Character(name="Hero", health=10)
    
    char.take_damage(100)
    assert char.health == 0, "Health should not drop below zero even with excessive damage."