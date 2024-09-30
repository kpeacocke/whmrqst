import pytest

# Mock classes for Reputation System

class ReputationSystem:
    def __init__(self):
        self.reputation = {}  # Dictionary to hold faction reputations
        self.max_reputation = 100
        self.min_reputation = -100

    def add_faction(self, faction):
        """Initialize reputation for a faction."""
        self.reputation[faction] = 0

    def modify_reputation(self, faction, amount):
        """Increase or decrease the reputation for a faction, within bounds."""
        if faction in self.reputation:
            self.reputation[faction] += amount
            # Enforce reputation bounds
            if self.reputation[faction] > self.max_reputation:
                self.reputation[faction] = self.max_reputation
            elif self.reputation[faction] < self.min_reputation:
                self.reputation[faction] = self.min_reputation

    def get_reputation(self, faction):
        """Return the current reputation for a faction."""
        return self.reputation.get(faction, 0)

    def check_reputation_threshold(self, faction, threshold):
        """Check if a faction's reputation meets a specific threshold."""
        return self.reputation.get(faction, 0) >= threshold


# Test cases for Reputation System

def test_modify_reputation():
    # Scenario 1: Ensure reputation can be increased or decreased
    rep_system = ReputationSystem()
    rep_system.add_faction("Merchants Guild")
    
    # Increase reputation
    rep_system.modify_reputation("Merchants Guild", 20)
    assert rep_system.get_reputation("Merchants Guild") == 20, "Reputation should increase by 20."

    # Decrease reputation
    rep_system.modify_reputation("Merchants Guild", -10)
    assert rep_system.get_reputation("Merchants Guild") == 10, "Reputation should decrease by 10."

def test_reputation_bounds():
    # Scenario 2: Ensure reputation is capped within defined bounds
    rep_system = ReputationSystem()
    rep_system.add_faction("Warriors Guild")
    
    # Increase reputation beyond max
    rep_system.modify_reputation("Warriors Guild", 150)
    assert rep_system.get_reputation("Warriors Guild") == 100, "Reputation should be capped at 100."

    # Decrease reputation below min
    rep_system.modify_reputation("Warriors Guild", -250)
    assert rep_system.get_reputation("Warriors Guild") == -100, "Reputation should be capped at -100."

def test_independent_faction_reputation():
    # Scenario 3: Ensure factions track their own reputation independently
    rep_system = ReputationSystem()
    rep_system.add_faction("Merchants Guild")
    rep_system.add_faction("Thieves Guild")

    # Modify reputation for one faction
    rep_system.modify_reputation("Merchants Guild", 30)
    assert rep_system.get_reputation("Merchants Guild") == 30, "Merchants Guild reputation should be updated independently."
    assert rep_system.get_reputation("Thieves Guild") == 0, "Thieves Guild reputation should remain unchanged."

def test_reputation_thresholds():
    # Scenario 4: Ensure reputation thresholds trigger specific outcomes
    rep_system = ReputationSystem()
    rep_system.add_faction("Merchants Guild")
    
    # Increase reputation to reach threshold
    rep_system.modify_reputation("Merchants Guild", 50)
    assert rep_system.check_reputation_threshold("Merchants Guild", 50), "Reputation threshold of 50 should be met."

    # Threshold should not be met if reputation is lower
    rep_system.modify_reputation("Merchants Guild", -10)
    assert not rep_system.check_reputation_threshold("Merchants Guild", 50), "Reputation threshold should no longer be met after lowering reputation."

def test_rival_factions_reputation():
    # Scenario 5: Ensure that actions affecting one faction can also affect another (rival factions)
    rep_system = ReputationSystem()
    rep_system.add_faction("Knights Guild")
    rep_system.add_faction("Outlaws")

    # Increase reputation with Knights, decrease with Outlaws (rival factions)
    rep_system.modify_reputation("Knights Guild", 40)
    rep_system.modify_reputation("Outlaws", -40)
    
    assert rep_system.get_reputation("Knights Guild") == 40, "Knights Guild reputation should increase by 40."
    assert rep_system.get_reputation("Outlaws") == -40, "Outlaws reputation should decrease by 40."