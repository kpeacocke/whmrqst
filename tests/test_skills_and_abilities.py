import pytest

# Mock classes for Skills and Abilities

class Skill:
    def __init__(self, name, level=1, max_level=5):
        self.name = name
        self.level = level
        self.max_level = max_level

    def level_up(self):
        """Increase the skill level, capped at the maximum level."""
        if self.level < self.max_level:
            self.level += 1

class Ability:
    def __init__(self, name, cooldown, effect):
        self.name = name
        self.cooldown = cooldown
        self.effect = effect
        self.cooldown_remaining = 0

    def use(self):
        """Use the ability if it's not on cooldown."""
        if self.cooldown_remaining == 0:
            self.cooldown_remaining = self.cooldown
            return self.effect
        else:
            return None

    def reduce_cooldown(self):
        """Reduce the cooldown timer (simulating time passing)."""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

class PassiveSkill(Skill):
    def apply_passive_effect(self, player):
        """Apply a passive effect based on skill level (e.g., stat boost)."""
        player.health += self.level * 10  # Example effect: increase health

class Player:
    def __init__(self, health=100):
        self.health = health
        self.skills = {}
        self.abilities = {}

    def learn_skill(self, skill):
        """Add a new skill to the player."""
        self.skills[skill.name] = skill

    def learn_ability(self, ability):
        """Add a new ability to the player."""
        self.abilities[ability.name] = ability


# Test cases for Skills and Abilities

def test_learn_skill():
    # Scenario 1: Ensure that skills can be learned
    player = Player()
    skill = Skill(name="Sword Mastery")
    
    player.learn_skill(skill)
    assert "Sword Mastery" in player.skills, "Player should have learned Sword Mastery skill."

def test_level_up_skill():
    # Scenario 2: Ensure that skills can be leveled up
    skill = Skill(name="Archery", level=1, max_level=5)
    
    skill.level_up()
    assert skill.level == 2, "Skill level should be 2 after leveling up."

    # Try to level up beyond max level
    for _ in range(10):  # Try leveling up 10 times
        skill.level_up()
    
    assert skill.level == 5, "Skill level should be capped at max level (5)."

def test_ability_use_and_effect():
    # Scenario 3: Ensure that abilities can be used and have the expected effect
    ability = Ability(name="Fireball", cooldown=3, effect="Deal 50 damage")
    
    effect = ability.use()
    assert effect == "Deal 50 damage", "Ability should deal 50 damage when used."

    # Ability should now be on cooldown
    assert ability.cooldown_remaining == 3, "Ability should be on cooldown after use."

def test_ability_cooldown():
    # Scenario 4: Ensure that abilities respect cooldowns
    ability = Ability(name="Heal", cooldown=2, effect="Heal 30 health")
    
    ability.use()  # Use the ability
    assert ability.cooldown_remaining == 2, "Cooldown should be 2 after using the ability."

    # Try to use the ability again while it's on cooldown
    assert ability.use() is None, "Ability should not be usable while on cooldown."

    # Reduce cooldown and try again
    ability.reduce_cooldown()
    assert ability.cooldown_remaining == 1, "Cooldown should reduce by 1 after time passes."

    ability.reduce_cooldown()
    assert ability.cooldown_remaining == 0, "Cooldown should be 0, ability should be usable again."

def test_passive_skill():
    # Scenario 5: Ensure that passive skills behave as expected
    player = Player(health=100)
    passive_skill = PassiveSkill(name="Fortitude", level=3)
    
    passive_skill.apply_passive_effect(player)
    assert player.health == 130, "Player health should increase by 30 due to passive skill effect."

def test_learning_and_using_skills_and_abilities():
    # Scenario 1 & 3: Ensure that skills and abilities can be learned and used correctly
    player = Player()
    
    # Learn and use a skill
    skill = Skill(name="Shield Block", level=1)
    player.learn_skill(skill)
    assert "Shield Block" in player.skills, "Player should have learned Shield Block skill."

    # Learn and use an ability
    ability = Ability(name="Lightning Strike", cooldown=1, effect="Deal 100 damage")
    player.learn_ability(ability)
    assert "Lightning Strike" in player.abilities, "Player should have learned Lightning Strike ability."
    
    # Safely check if the ability exists before using it
    if "Lightning Strike" in player.abilities:
        effect = player.abilities["Lightning Strike"].use()
        assert effect == "Deal 100 damage", "Player should use Lightning Strike to deal 100 damage."
    else:
        pytest.fail("Player has not learned Lightning Strike ability.")