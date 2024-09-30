import pytest

# Mock classes for Target Audience System

class TargetAudienceSystem:
    def __init__(self, player_age, player_region, player_experience):
        self.player_age = player_age
        self.player_region = player_region
        self.player_experience = player_experience

    def get_content_for_age_group(self):
        """Deliver content based on the player's age group."""
        if self.player_age < 13:
            return "Child-friendly content"
        elif 13 <= self.player_age < 18:
            return "Teen content"
        else:
            return "Adult content"

    def get_localized_message(self):
        """Deliver localized messages based on the player's region."""
        messages = {
            "US": "Hello!",
            "FR": "Bonjour!",
            "JP": "こんにちは!"
        }
        return messages.get(self.player_region, "Hello!")

    def adjust_difficulty(self):
        """Adjust gameplay difficulty based on player experience."""
        if self.player_experience == "casual":
            return "Easy Mode"
        elif self.player_experience == "hardcore":
            return "Hard Mode"
        return "Normal Mode"

    def check_content_restriction(self):
        """Apply content restrictions based on age (e.g., for mature content)."""
        if self.player_age < 18:
            return "Restricted content"
        return "Unrestricted content"

    def adapt_user_interface(self):
        """Adapt the UI based on the player's age group (simplified UI for younger players)."""
        if self.player_age < 13:
            return "Simplified UI"
        return "Standard UI"

# Test cases for Target Audience

def test_content_for_age_group():
    # Scenario 1: Ensure that content is delivered based on the player's age group
    audience_system = TargetAudienceSystem(player_age=10, player_region="US", player_experience="casual")
    assert audience_system.get_content_for_age_group() == "Child-friendly content", "Content should be child-friendly for players under 13."

    audience_system = TargetAudienceSystem(player_age=16, player_region="US", player_experience="casual")
    assert audience_system.get_content_for_age_group() == "Teen content", "Content should be for teens for players aged 13-17."

    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="casual")
    assert audience_system.get_content_for_age_group() == "Adult content", "Content should be adult for players aged 18 and over."

def test_localized_message():
    # Scenario 2: Ensure localized messages are shown based on the player's region
    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="casual")
    assert audience_system.get_localized_message() == "Hello!", "Localized message should be 'Hello!' for the US region."

    audience_system = TargetAudienceSystem(player_age=25, player_region="FR", player_experience="casual")
    assert audience_system.get_localized_message() == "Bonjour!", "Localized message should be 'Bonjour!' for the French region."

    audience_system = TargetAudienceSystem(player_age=25, player_region="JP", player_experience="casual")
    assert audience_system.get_localized_message() == "こんにちは!", "Localized message should be 'こんにちは!' for the Japanese region."

def test_adjust_difficulty():
    # Scenario 3: Ensure difficulty is adjusted based on player experience
    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="casual")
    assert audience_system.adjust_difficulty() == "Easy Mode", "Difficulty should be 'Easy Mode' for casual players."

    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="hardcore")
    assert audience_system.adjust_difficulty() == "Hard Mode", "Difficulty should be 'Hard Mode' for hardcore players."

    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="normal")
    assert audience_system.adjust_difficulty() == "Normal Mode", "Difficulty should be 'Normal Mode' for normal players."

def test_content_restrictions():
    # Scenario 4: Ensure content restrictions are applied based on the player's age
    audience_system = TargetAudienceSystem(player_age=16, player_region="US", player_experience="casual")
    assert audience_system.check_content_restriction() == "Restricted content", "Players under 18 should have restricted content."

    audience_system = TargetAudienceSystem(player_age=25, player_region="US", player_experience="casual")
    assert audience_system.check_content_restriction() == "Unrestricted content", "Players 18 and over should have unrestricted content."

def test_adapt_user_interface():
    # Scenario 5: Ensure UI is adapted based on the player's age group
    audience_system = TargetAudienceSystem(player_age=10, player_region="US", player_experience="casual")
    assert audience_system.adapt_user_interface() == "Simplified UI", "UI should be simplified for players under 13."

    audience_system = TargetAudienceSystem(player_age=20, player_region="US", player_experience="casual")
    assert audience_system.adapt_user_interface() == "Standard UI", "UI should be standard for players 13 and older."