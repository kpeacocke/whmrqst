import pytest

# Mock classes for Quest Types

class Quest:
    def __init__(self, name):
        self.name = name
        self.completed = False
        self.failed = False

    def check_completion(self):
        pass  # Base method for checking completion

    def fail_quest(self):
        """Mark the quest as failed."""
        self.failed = True


class FetchQuest(Quest):
    def __init__(self, name, required_items):
        super().__init__(name)
        self.required_items = required_items
        self.collected_items = {}

    def collect_item(self, item, quantity):
        if item in self.required_items:
            if item in self.collected_items:
                self.collected_items[item] += quantity
            else:
                self.collected_items[item] = quantity
        self.check_completion()

    def check_completion(self):
        """Check if all required items are collected."""
        if all(item in self.collected_items and self.collected_items[item] >= qty for item, qty in self.required_items.items()):
            self.completed = True


class KillQuest(Quest):
    def __init__(self, name, required_enemies):
        super().__init__(name)
        self.required_enemies = required_enemies
        self.killed_enemies = {}

    def kill_enemy(self, enemy, quantity=1):
        if enemy in self.required_enemies:
            if enemy in self.killed_enemies:
                self.killed_enemies[enemy] += quantity
            else:
                self.killed_enemies[enemy] = quantity
        self.check_completion()

    def check_completion(self):
        """Check if all required enemies are killed."""
        if all(enemy in self.killed_enemies and self.killed_enemies[enemy] >= qty for enemy, qty in self.required_enemies.items()):
            self.completed = True


class EscortQuest(Quest):
    def __init__(self, name, npc):
        super().__init__(name)
        self.npc = npc
        self.npc_alive = True
        self.npc_at_destination = False

    def npc_reaches_destination(self):
        """Mark the NPC as having reached the destination."""
        if self.npc_alive:
            self.npc_at_destination = True
            self.check_completion()

    def npc_dies(self):
        """Fail the quest if the NPC dies."""
        self.npc_alive = False
        self.fail_quest()

    def check_completion(self):
        """Check if the NPC has safely reached the destination."""
        if self.npc_alive and self.npc_at_destination:
            self.completed = True


# Test cases for Quest Types

def test_fetch_quest_completion():
    # Scenario 1: Ensure a fetch quest is completed when required items are collected
    required_items = {"Herbs": 10, "Potion": 1}
    quest = FetchQuest(name="Herbalist's Fetch Quest", required_items=required_items)
    
    quest.collect_item("Herbs", 5)
    assert not quest.completed, "Quest should not be completed if all items are not collected."

    quest.collect_item("Herbs", 5)
    quest.collect_item("Potion", 1)
    
    assert quest.completed, "Quest should be completed when all required items are collected."

def test_kill_quest_completion():
    # Scenario 2: Ensure a kill quest is completed when required enemies are killed
    required_enemies = {"Goblin": 5, "Orc": 3}
    quest = KillQuest(name="Orc Slayer", required_enemies=required_enemies)
    
    quest.kill_enemy("Goblin", 3)
    assert not quest.completed, "Quest should not be completed if all enemies are not killed."

    quest.kill_enemy("Goblin", 2)
    quest.kill_enemy("Orc", 3)
    
    assert quest.completed, "Quest should be completed when all required enemies are killed."

def test_escort_quest_completion():
    # Scenario 3: Ensure an escort quest is completed when the NPC reaches the destination
    quest = EscortQuest(name="Escort the Merchant", npc="Merchant")
    
    quest.npc_reaches_destination()
    
    assert quest.completed, "Quest should be completed when the NPC safely reaches the destination."

def test_escort_quest_failure():
    # Scenario 4: Ensure escort quests fail if the NPC dies
    quest = EscortQuest(name="Escort the Merchant", npc="Merchant")
    
    quest.npc_dies()
    
    assert quest.failed, "Quest should fail if the NPC dies."
    assert not quest.completed, "Quest should not be completed if the NPC dies."

def test_independent_quest_tracking():
    # Scenario 5: Ensure different quest types are tracked and completed independently
    fetch_quest = FetchQuest(name="Herbalist's Fetch Quest", required_items={"Herbs": 10, "Potion": 1})
    kill_quest = KillQuest(name="Orc Slayer", required_enemies={"Orc": 3})

    fetch_quest.collect_item("Herbs", 10)
    fetch_quest.collect_item("Potion", 1)
    kill_quest.kill_enemy("Orc", 3)

    assert fetch_quest.completed, "Fetch quest should be completed when all items are collected."
    assert kill_quest.completed, "Kill quest should be completed when all enemies are killed."