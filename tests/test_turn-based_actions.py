import pytest

# Custom exceptions
class InvalidTurnError(Exception):
    pass

class ActionAlreadyTakenError(Exception):
    pass

# Mock functions or classes for the game
class Game:
    def __init__(self):
        self.turn_order = ["player1", "player2"]
        self.current_turn = 0
        self.actions_taken = {}

    def get_current_turn(self):
        return self.turn_order[self.current_turn]

    def take_action(self, player_id, action):
        if player_id != self.get_current_turn():
            raise InvalidTurnError(f"It's not {player_id}'s turn!")
        if player_id in self.actions_taken:
            raise ActionAlreadyTakenError(f"{player_id} has already taken an action this turn!")
        self.actions_taken[player_id] = action

    def end_turn(self):
        self.actions_taken = {}
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)

# Test cases for Turn-Based Actions

def test_player_can_take_one_action_per_turn():
    # Setup
    game = Game()
    player = game.get_current_turn()
    
    # Player takes an action
    game.take_action(player, "attack")
    
    # Try to take a second action in the same turn, should raise an exception
    with pytest.raises(Exception, match=f"{player} has already taken an action this turn!"):
        game.take_action(player, "defend")

def test_turn_order_is_followed():
    # Setup
    game = Game()
    
    # Player 1 takes an action
    game.take_action("player1", "attack")
    game.end_turn()
    
    # It's now player 2's turn, player 1 should not be able to act
    with pytest.raises(Exception, match="It's not player1's turn!"):
        game.take_action("player1", "attack")
    
    # Player 2 should be able to act
    game.take_action("player2", "defend")
    game.end_turn()

def test_turn_order_is_reset_after_last_player():
    # Setup
    game = Game()
    
    # Player 1 takes an action and ends turn
    game.take_action("player1", "attack")
    game.end_turn()
    
    # Player 2 takes an action and ends turn
    game.take_action("player2", "defend")
    game.end_turn()
    
    # Player 1's turn should start again
    assert game.get_current_turn() == "player1"