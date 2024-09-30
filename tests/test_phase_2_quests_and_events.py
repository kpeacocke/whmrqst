import pytest

# Mock classes for Quests and Events

class Quest:
    def __init__(self, name, stages, reward):
        self.name = name
        self.stages = stages
        self.current_stage = 0
        self.completed = False
        self.reward = reward

    def progress(self):
        """Progress to the next stage of the quest."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
        else:
            self.complete_quest()

    def complete_quest(self):
        """Complete the quest."""
        self.completed = True

    def get_current_stage(self):
        """Return the current stage of the quest."""
        return self.stages[self.current_stage]

    def is_completed(self):
        """Return whether the quest is completed."""
        return self.completed

    def get_reward(self):
        """Return the reward for completing the quest."""
        if self.is_completed():
            return self.reward
        return None


class Event:
    def __init__(self, name, trigger_condition, effect):
        self.name = name
        self.trigger_condition = trigger_condition  # A function that returns True if the event should trigger
        self.effect = effect
        self.triggered = False

    def check_trigger(self, game_state):
        """Check if the event should trigger."""
        if self.trigger_condition(game_state) and not self.triggered:
            self.trigger()
            return True
        return False

    def trigger(self):
        """Trigger the event and apply its effect."""
        self.triggered = True
        self.effect()


# Test cases for Phase 2 Quests and Events

# Quest System

def test_add_and_complete_quest():
    # Ensure that a quest can be added and completed
    quest = Quest(name="Find the Lost Sword", stages=["Start", "Find Clue", "Retrieve Sword"], reward="100 Gold")
    
    assert quest.get_current_stage() == "Start", "Quest should start at the 'Start' stage."
    
    quest.progress()
    assert quest.get_current_stage() == "Find Clue", "Quest should progress to 'Find Clue' stage."
    
    quest.progress()
    assert quest.get_current_stage() == "Retrieve Sword", "Quest should progress to 'Retrieve Sword' stage."
    
    quest.progress()
    assert quest.is_completed(), "Quest should be completed after progressing through all stages."
    assert quest.get_reward() == "100 Gold", "Quest should grant '100 Gold' as a reward."

def test_multi_stage_quest_progress():
    # Ensure multi-stage quests progress properly
    quest = Quest(name="Save the Village", stages=["Investigate", "Defeat Bandits", "Return to Village"], reward="Village's Gratitude")
    
    quest.progress()
    assert quest.get_current_stage() == "Defeat Bandits", "Quest should progress to 'Defeat Bandits' stage."
    
    quest.progress()
    assert quest.get_current_stage() == "Return to Village", "Quest should progress to 'Return to Village' stage."
    
    quest.progress()
    assert quest.is_completed(), "Quest should be completed after all stages are completed."

def test_quest_incomplete_no_reward():
    # Ensure no reward is given if quest is not completed
    quest = Quest(name="Deliver the Message", stages=["Start", "Deliver"], reward="50 Gold")
    
    assert quest.get_reward() is None, "No reward should be given before the quest is completed."
    
    quest.progress()
    assert quest.get_reward() is None, "Still no reward should be given if the quest is incomplete."

# Random Events

def test_trigger_random_event():
    # Ensure that random events trigger based on conditions
    game_state = {"gold": 100, "weather": "sunny"}
    
    def trigger_if_rich(state):
        return state["gold"] >= 100
    
    def gain_armor():
        game_state["armor"] = "Steel Armor"
    
    event = Event(name="Find Armor", trigger_condition=trigger_if_rich, effect=gain_armor)
    
    assert not event.triggered, "Event should not be triggered at the start."
    
    event.check_trigger(game_state)
    assert event.triggered, "Event should trigger if the player has enough gold."
    assert game_state["armor"] == "Steel Armor", "Player should gain 'Steel Armor' after the event."

def test_event_does_not_trigger_multiple_times():
    # Ensure that random events don't trigger multiple times
    game_state = {"gold": 100}
    
    def trigger_if_rich(state):
        return state["gold"] >= 100
    
    def gain_armor():
        game_state["armor"] = "Steel Armor"
    
    event = Event(name="Find Armor", trigger_condition=trigger_if_rich, effect=gain_armor)
    
    event.check_trigger(game_state)
    assert event.triggered, "Event should trigger the first time."
    
    # Simulate passing the same game state again
    event.check_trigger(game_state)
    assert game_state["armor"] == "Steel Armor", "Event should not trigger again and armor should remain the same."

# Timed Events

def test_timed_event_trigger():
    # Ensure that events trigger at specific moments in the game (e.g., based on time or day)
    game_state = {"day": 5}
    
    def trigger_on_day_five(state):
        return state["day"] == 5
    
    def change_weather():
        game_state["weather"] = "rainy"
    
    event = Event(name="Rainy Day", trigger_condition=trigger_on_day_five, effect=change_weather)
    
    event.check_trigger(game_state)
    assert event.triggered, "Event should trigger on day 5."
    assert game_state["weather"] == "rainy", "Weather should change to 'rainy' after the event."

def test_event_with_no_condition_does_not_trigger():
    # Ensure that an event does not trigger if the condition is not met
    game_state = {"gold": 50}
    
    def trigger_if_rich(state):
        return state["gold"] >= 100
    
    def find_gold():
        game_state["gold"] += 50
    
    event = Event(name="Find Gold", trigger_condition=trigger_if_rich, effect=find_gold)
    
    event.check_trigger(game_state)
    assert not event.triggered, "Event should not trigger if the condition is not met."