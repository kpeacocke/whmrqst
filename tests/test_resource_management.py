import pytest

# Mock classes for Resource Management

class ResourceManagement:
    def __init__(self, resource_limits=None):
        self.resources = {}
        self.resource_limits = resource_limits or {}  # Dictionary for resource limits

    def add_resource(self, resource, amount):
        """Add a specific amount to a resource."""
        if resource not in self.resources:
            self.resources[resource] = 0
        self.resources[resource] += amount
        
        # Check if the resource exceeds its maximum capacity
        if resource in self.resource_limits:
            if self.resources[resource] > self.resource_limits[resource]:
                self.resources[resource] = self.resource_limits[resource]

    def consume_resource(self, resource, amount):
        """Consume a specific amount of a resource. It cannot drop below zero."""
        if resource not in self.resources:
            self.resources[resource] = 0
        self.resources[resource] -= amount
        
        # Ensure the resource doesn't go below zero
        if self.resources[resource] < 0:
            self.resources[resource] = 0

    def get_resource(self, resource):
        """Get the current amount of a specific resource."""
        return self.resources.get(resource, 0)

    def set_resource_limit(self, resource, limit):
        """Set the maximum limit for a specific resource."""
        self.resource_limits[resource] = limit

# Test cases for Resource Management

def test_add_resource():
    # Scenario 1: Ensure resources can be added
    rm = ResourceManagement()
    rm.add_resource("gold", 100)
    assert rm.get_resource("gold") == 100, "Gold resource should be 100 after adding 100."
    
    # Add more gold
    rm.add_resource("gold", 50)
    assert rm.get_resource("gold") == 150, "Gold resource should be 150 after adding another 50."

def test_consume_resource():
    # Scenario 1: Ensure resources can be consumed correctly
    rm = ResourceManagement()
    rm.add_resource("food", 100)
    
    rm.consume_resource("food", 30)
    assert rm.get_resource("food") == 70, "Food should be 70 after consuming 30."

    # Consume more food than available
    rm.consume_resource("food", 80)
    assert rm.get_resource("food") == 0, "Food should not drop below 0 after overconsumption."

def test_resource_limits():
    # Scenario 2: Ensure resources cannot exceed a defined maximum capacity
    rm = ResourceManagement(resource_limits={"wood": 100})
    
    # Add wood within the limit
    rm.add_resource("wood", 50)
    assert rm.get_resource("wood") == 50, "Wood should be 50 after adding 50."
    
    # Add more wood, exceeding the limit
    rm.add_resource("wood", 70)
    assert rm.get_resource("wood") == 100, "Wood should be capped at 100 (the limit)."

def test_no_negative_resources():
    # Scenario 3: Ensure resources cannot drop below zero
    rm = ResourceManagement()
    
    # Try to consume a resource that hasn't been added yet
    rm.consume_resource("energy", 50)
    assert rm.get_resource("energy") == 0, "Energy should be 0 as it can't drop below 0."

def test_multi_resource_management():
    # Scenario 4: Ensure multiple resources are managed correctly
    rm = ResourceManagement()
    rm.add_resource("gold", 200)
    rm.add_resource("stone", 300)
    
    # Consume resources
    rm.consume_resource("gold", 100)
    rm.consume_resource("stone", 150)
    
    assert rm.get_resource("gold") == 100, "Gold should be 100 after consumption."
    assert rm.get_resource("stone") == 150, "Stone should be 150 after consumption."

def test_resource_production():
    # Scenario 5: Ensure resources can be produced over time (simple simulation)
    rm = ResourceManagement()
    rm.add_resource("water", 50)
    
    # Simulate production over time (e.g., every hour)
    for _ in range(5):  # Simulate 5 hours of water production (10 units per hour)
        rm.add_resource("water", 10)
    
    assert rm.get_resource("water") == 100, "Water should be 100 after 5 hours of production (10 units/hour)."

def test_resource_limits_with_production():
    # Scenario 5: Ensure production is limited by resource limits
    rm = ResourceManagement(resource_limits={"water": 100})
    rm.add_resource("water", 80)
    
    # Simulate production over time (e.g., every hour)
    for _ in range(3):  # Simulate 3 hours of water production (10 units per hour)
        rm.add_resource("water", 10)
    
    assert rm.get_resource("water") == 100, "Water should be capped at 100 (the limit) after production."