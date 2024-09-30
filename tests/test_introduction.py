import pytest

# Mock Introduction and Game classes for testing purposes
class Introduction:
    def __init__(self):
        self.completed = False
        self.tutorial_step = 0
        self.tutorial_steps = ["Move character", "Attack", "Open inventory"]

    def start(self):
        """Start the introduction sequence."""
        self.tutorial_step = 1  # Starting with the first tutorial step

    def next_step(self):
        """Move to the next step of the tutorial."""
        if self.tutorial_step < len(self.tutorial_steps):
            self.tutorial_step += 1

        if self.tutorial_step == len(self.tutorial_steps):
            self.completed = True

class Game:
    def __init__(self):
        self.started = False

    def start_game(self):
        """Start the main game after the introduction."""
        self.started = True

# Test cases for Introduction

def test_introduction_initialization():
    # Scenario 1: Ensure the introduction initializes correctly
    intro = Introduction()
    
    assert intro.tutorial_step == 0, "Introduction should start with tutorial step 0."
    assert not intro.completed, "Introduction should not be completed at the start."

def test_tutorial_progression():
    # Scenario 2: Ensure tutorial steps progress correctly
    intro = Introduction()
    
    intro.start()
    assert intro.tutorial_step == 1, "After starting, tutorial should be at step 1."
    
    intro.next_step()
    assert intro.tutorial_step == 2, "Tutorial should progress to step 2."
    
    intro.next_step()
    assert intro.tutorial_step == 3, "Tutorial should progress to step 3."
    assert intro.completed, "Tutorial should be marked as completed after the last step."

def test_tutorial_interaction():
    # Scenario 3: Ensure tutorial interaction allows progression
    intro = Introduction()
    intro.start()

    assert intro.tutorial_steps[intro.tutorial_step - 1] == "Move character", "First step should be 'Move character'."
    
    intro.next_step()
    assert intro.tutorial_steps[intro.tutorial_step - 1] == "Attack", "Second step should be 'Attack'."
    
    intro.next_step()
    assert intro.tutorial_steps[intro.tutorial_step - 1] == "Open inventory", "Third step should be 'Open inventory'."

def test_introduction_to_game_transition():
    # Scenario 4: Ensure the game starts after the introduction is completed
    intro = Introduction()
    game = Game()

    # Complete the introduction
    intro.start()
    while not intro.completed:
        intro.next_step()

    assert intro.completed, "Introduction should be completed before starting the game."
    
    # Start the game
    game.start_game()
    
    assert game.started, "Game should start after the introduction is completed."