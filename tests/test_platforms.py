import pytest

# Mock classes for Platforms and Player
class Platform:
    def __init__(self, name):
        self.name = name

    def interact(self, player):
        pass  # Base method for interaction

class StaticPlatform(Platform):
    def __init__(self):
        super().__init__(name="StaticPlatform")
        self.height = 0  # Platform is at height 0

    def detect_collision(self, player):
        """Check if the player is at or below the platform's height."""
        if player.position >= self.height:
            return True
        return False

    def interact(self, player):
        if self.detect_collision(player):
            player.standing_on_platform = True  # Simulate player standing on platform

class MovingPlatform(Platform):
    def __init__(self, speed):
        super().__init__(name="MovingPlatform")
        self.speed = speed
        self.position = 0

    def move(self):
        """Move the platform."""
        self.position += self.speed

    def interact(self, player):
        player.position += self.speed  # Move player with the platform

class DestructiblePlatform(Platform):
    def __init__(self):
        super().__init__(name="DestructiblePlatform")
        self.is_destroyed = False

    def interact(self, player):
        self.is_destroyed = True  # Simulate platform breaking

class TriggerPlatform(Platform):
    def __init__(self, trigger_action):
        super().__init__(name="TriggerPlatform")
        self.trigger_action = trigger_action

    def interact(self, player):
        self.trigger_action()  # Simulate triggering an action

# Mock Player class for testing interaction with platforms
class Player:
    def __init__(self, name):
        self.name = name
        self.standing_on_platform = False
        self.position = 0

# Test cases for Platforms

def test_static_platform():
    # Scenario 1: Ensure player can stand on a static platform
    player = Player(name="Player1")
    platform = StaticPlatform()
    
    platform.interact(player)
    
    assert player.standing_on_platform, "Player should be standing on the static platform."

def test_moving_platform():
    # Scenario 2: Ensure moving platforms function correctly
    player = Player(name="Player1")
    platform = MovingPlatform(speed=5)
    
    initial_position = player.position
    platform.move()
    platform.interact(player)
    
    assert platform.position == 5, "Moving platform should move to position 5."
    assert player.position == initial_position + 5, "Player should move along with the platform."

def test_destructible_platform():
    # Scenario 3: Ensure destructible platforms break after interaction
    player = Player(name="Player1")
    platform = DestructiblePlatform()
    
    platform.interact(player)
    
    assert platform.is_destroyed, "Destructible platform should break after interaction."

def test_trigger_platform():
    # Scenario 4: Ensure event-triggering platforms work correctly
    player = Player(name="Player1")
    event_triggered = [False]  # Using a list to mutate the value in the inner function

    def trigger_event():
        event_triggered[0] = True

    platform = TriggerPlatform(trigger_action=trigger_event)
    
    platform.interact(player)
    
    assert event_triggered[0], "Event should be triggered when stepping on the platform."

def test_collision_detection_with_platform():
    # Scenario 5: Ensure platform handles collision detection correctly
    player = Player(name="Player1")
    platform = StaticPlatform()
    
    # Simulate the player above and below the platform
    player.position = -5  # Simulate below the platform
    assert not platform.detect_collision(player), "Player should not collide with platform when below it."

    # Simulate the player falling onto the platform
    player.position = 10  # Simulate above the platform
    assert platform.detect_collision(player), "Player should collide with platform when falling onto it."

    platform.interact(player)
    assert player.standing_on_platform, "Player should be standing on the platform after collision."