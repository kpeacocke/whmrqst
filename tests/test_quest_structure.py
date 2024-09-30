import pytest

# Mock classes for Quest and QuestSystem
class Quest:
    def __init__(self, name, objectives):
        self.name = name
        self.objectives = objectives  # List of objectives (dict: {"description": str, "completed": bool})
        self.completed = False
        self.failed = False

    def complete_objective(self, objective_index):
        """Complete a specific quest objective."""
        if 0 <= objective_index < len(self.objectives):
            self.objectives[objective_index]["completed"] = True
            self.check_completion()

    def check_completion(self):
        """Check if all objectives are completed and mark the quest as completed."""
        if all(obj["completed"] for obj in self.objectives):
            self.completed = True

    def fail_quest(self):
        """Mark the quest as failed."""
        self.failed = True

class QuestSystem:
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []
        self.failed_quests = []

    def add_quest(self, quest):
        """Add a quest to the active quests list."""
        self.active_quests.append(quest)

    def complete_quest(self, quest):
        """Move a quest to the completed quests list."""
        if quest.completed:
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)

    def fail_quest(self, quest):
        """Move a quest to the failed quests list."""
        if quest.failed:
            self.active_quests.remove(quest)
            self.failed_quests.append(quest)


# Test cases for Quest Structure

def test_quest_initialization():
    # Scenario 1: Ensure a quest is correctly initialized with objectives
    objectives = [{"description": "Collect 10 herbs", "completed": False},
                  {"description": "Defeat the forest monster", "completed": False}]
    quest = Quest(name="Herbalist's Task", objectives=objectives)
    
    assert quest.name == "Herbalist's Task", "Quest should be initialized with the correct name."
    assert len(quest.objectives) == 2, "Quest should have 2 objectives."
    assert not quest.completed, "Quest should not be completed at initialization."
    assert not quest.failed, "Quest should not be marked as failed at initialization."

def test_complete_quest_objective():
    # Scenario 2: Ensure quest objectives can be completed and progress is tracked
    objectives = [{"description": "Collect 10 herbs", "completed": False},
                  {"description": "Defeat the forest monster", "completed": False}]
    quest = Quest(name="Herbalist's Task", objectives=objectives)
    
    quest.complete_objective(0)  # Complete the first objective
    assert quest.objectives[0]["completed"], "First objective should be marked as completed."
    assert not quest.completed, "Quest should not be marked as completed if not all objectives are done."

    quest.complete_objective(1)  # Complete the second objective
    assert quest.objectives[1]["completed"], "Second objective should be marked as completed."
    assert quest.completed, "Quest should be marked as completed when all objectives are done."

def test_complete_quest():
    # Scenario 3: Ensure a quest can be completed and moved to completed quests
    objectives = [{"description": "Collect 10 herbs", "completed": False}]
    quest = Quest(name="Herbalist's Task", objectives=objectives)
    quest_system = QuestSystem()

    quest_system.add_quest(quest)
    assert quest in quest_system.active_quests, "Quest should be in the active quests list."

    # Complete the objective and mark quest as completed
    quest.complete_objective(0)
    quest_system.complete_quest(quest)

    assert quest not in quest_system.active_quests, "Quest should be removed from active quests after completion."
    assert quest in quest_system.completed_quests, "Quest should be moved to completed quests."

def test_fail_quest():
    # Scenario 4: Ensure a quest can be failed and moved to failed quests
    objectives = [{"description": "Collect 10 herbs", "completed": False}]
    quest = Quest(name="Herbalist's Task", objectives=objectives)
    quest_system = QuestSystem()

    quest_system.add_quest(quest)
    assert quest in quest_system.active_quests, "Quest should be in the active quests list."

    # Fail the quest
    quest.fail_quest()
    quest_system.fail_quest(quest)

    assert quest not in quest_system.active_quests, "Quest should be removed from active quests after failure."
    assert quest in quest_system.failed_quests, "Quest should be moved to failed quests."

def test_multi_stage_quest():
    # Scenario 5: Ensure multi-stage quests progress through stages properly
    objectives = [{"description": "Collect 10 herbs", "completed": False},
                  {"description": "Defeat the forest monster", "completed": False}]
    quest = Quest(name="Herbalist's Task", objectives=objectives)

    quest.complete_objective(0)  # Complete the first stage
    assert quest.objectives[0]["completed"], "First stage should be completed."
    assert not quest.completed, "Quest should not be fully completed after just one stage."

    quest.complete_objective(1)  # Complete the second stage
    assert quest.objectives[1]["completed"], "Second stage should be completed."
    assert quest.completed, "Quest should be marked as completed when all stages are done."