import pytest
import secrets

# Mock classes for Random Events

class RandomEventSystem:
    def __init__(self):
        self.events = []
        self.triggered_events = []

    def add_event(self, event, probability=1.0):
        """Add a random event with a probability (default is 1.0 for always triggering)."""
        self.events.append({"event": event, "probability": probability})

    def trigger_random_event(self):
        """Trigger a random event based on the probabilities."""
        available_events = [e for e in self.events if secrets.randbelow(100) / 100.0 < e["probability"]]
        if available_events:
            chosen_event = secrets.choice(available_events)
            chosen_event["event"]()
            self.triggered_events.append(chosen_event["event"])
            return chosen_event["event"]

    def reset_events(self):
        """Reset the list of triggered events for testing."""
        self.triggered_events.clear()


# Example events
def encounter_enemy():
    print("Enemy encountered!")

def find_treasure():
    print("Treasure found!")

def change_weather():
    print("Weather changed!")


# Test cases for Random Events

def test_trigger_random_event():
    # Scenario 1: Ensure that a random event can be triggered from a set of possible events
    event_system = RandomEventSystem()
    event_system.add_event(encounter_enemy)
    event_system.add_event(find_treasure)
    
    triggered_event = event_system.trigger_random_event()
    assert triggered_event in [encounter_enemy, find_treasure], "Triggered event should be one of the added events."

def test_event_probabilities():
    # Scenario 2: Ensure that random events are triggered based on probabilities
    event_system = RandomEventSystem()
    event_system.add_event(encounter_enemy, probability=0.0)  # Should never trigger
    event_system.add_event(find_treasure, probability=1.0)    # Should always trigger
    
    triggered_event = event_system.trigger_random_event()
    
    assert triggered_event == find_treasure, "The event with 100% probability should always trigger."
    event_system.reset_events()

    # Test with a small probability (might not trigger)
    event_system.add_event(encounter_enemy, probability=0.01)  # Very unlikely
    triggered_event = event_system.trigger_random_event()
    assert triggered_event is None, "Low probability event should not trigger often."

def test_unique_event():
    # Scenario 3: Ensure that unique random events do not repeat
    event_system = RandomEventSystem()
    
    def unique_event():
        print("Unique event triggered!")
    
    event_system.add_event(unique_event)
    
    # Trigger the unique event once
    triggered_event = event_system.trigger_random_event()
    assert triggered_event == unique_event, "Unique event should trigger the first time."
    
    # Reset events but remove the unique event to ensure it can't trigger again
    event_system.events.remove({"event": unique_event, "probability": 1.0})
    triggered_event = event_system.trigger_random_event()
    assert triggered_event != unique_event, "Unique event should not trigger again."

def test_random_event_affects_game_state():
    # Scenario 4: Ensure that random events can affect game state
    game_state = {"gold": 0, "enemies": 0, "weather": "sunny"}
    
    def gain_gold():
        game_state["gold"] += 100
    
    def spawn_enemy():
        game_state["enemies"] += 1
    
    def change_weather():
        game_state["weather"] = "rainy"
    
    event_system = RandomEventSystem()
    event_system.add_event(gain_gold)
    event_system.add_event(spawn_enemy)
    event_system.add_event(change_weather)
    
    # Trigger events and check game state changes
    event_system.trigger_random_event()
    
    # Check if one of the changes happened (as it's random which one happens)
    assert game_state["gold"] == 100 or game_state["enemies"] == 1 or game_state["weather"] == "rainy", "Game state should be affected by one of the random events."

def test_event_probabilities_respected():
    # Scenario 5: Ensure that random event probabilities are respected (e.g., rare events happen less frequently)
    event_system = RandomEventSystem()
    event_system.add_event(encounter_enemy, probability=0.1)  # Low chance event
    event_system.add_event(find_treasure, probability=0.9)    # High chance event

    event_count = {"enemy": 0, "treasure": 0}

    for _ in range(1000):
        event = event_system.trigger_random_event()
        if event == encounter_enemy:
            event_count["enemy"] += 1
        elif event == find_treasure:
            event_count["treasure"] += 1

    assert event_count["treasure"] > event_count["enemy"], "High chance events should trigger more frequently."