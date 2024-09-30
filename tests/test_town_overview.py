import pytest

# Mock classes for Town and TownOverview

class Town:
    def __init__(self, name, population, features=None):
        """Initialize a town with a name, population, and features."""
        self.name = name
        self.population = population
        self.features = features or []

    def add_feature(self, feature):
        """Add a new feature to the town."""
        self.features.append(feature)

    def update_population(self, new_population):
        """Update the population of the town."""
        self.population = new_population

class TownOverview:
    def __init__(self, town):
        self.town = town

    def display_overview(self):
        """Return a summary of the town."""
        overview = f"Town: {self.town.name}\n"
        overview += f"Population: {self.town.population}\n"
        overview += "Features: " + ", ".join(self.town.features) if self.town.features else "No features available."
        return overview

# Test cases for Town Overview

def test_town_overview_display():
    # Scenario 1: Ensure that the correct town overview is displayed
    town = Town(name="Eldoria", population=500, features=["shop", "inn"])
    overview = TownOverview(town)
    
    expected_output = "Town: Eldoria\nPopulation: 500\nFeatures: shop, inn"
    assert overview.display_overview() == expected_output, "Town overview should display the correct town details."

def test_town_features_in_overview():
    # Scenario 2: Ensure that town-specific features are correctly listed in the overview
    town = Town(name="Dunharrow", population=800, features=["blacksmith", "tavern"])
    overview = TownOverview(town)
    
    expected_output = "Town: Dunharrow\nPopulation: 800\nFeatures: blacksmith, tavern"
    assert overview.display_overview() == expected_output, "Town overview should list the correct features."

def test_town_population_update_in_overview():
    # Scenario 3: Ensure that changes to the town (population) are reflected in the overview
    town = Town(name="Eldoria", population=500)
    overview = TownOverview(town)

    # Update population
    town.update_population(600)
    expected_output = "Town: Eldoria\nPopulation: 600\nNo features available."
    assert overview.display_overview() == expected_output, "Town overview should reflect updated population."

def test_town_add_feature_in_overview():
    # Scenario 3: Ensure that new features are reflected in the overview
    town = Town(name="Eldoria", population=500)
    overview = TownOverview(town)

    # Add new feature
    town.add_feature("market")
    expected_output = "Town: Eldoria\nPopulation: 500\nFeatures: market"
    assert overview.display_overview() == expected_output, "Town overview should reflect added feature."

def test_town_special_event_in_overview():
    # Scenario 4: Ensure that special events or town upgrades are reflected in the overview
    town = Town(name="Eldoria", population=500, features=["inn"])
    overview = TownOverview(town)

    # Town holds a festival (add new feature)
    town.add_feature("festival")
    expected_output = "Town: Eldoria\nPopulation: 500\nFeatures: inn, festival"
    assert overview.display_overview() == expected_output, "Town overview should reflect special events like festivals."

def test_multiple_town_overviews():
    # Scenario 5: Ensure that multiple town overviews can be displayed correctly
    town1 = Town(name="Eldoria", population=500, features=["inn", "market"])
    town2 = Town(name="Dunharrow", population=800, features=["blacksmith", "tavern"])

    overview1 = TownOverview(town1)
    overview2 = TownOverview(town2)

    expected_output1 = "Town: Eldoria\nPopulation: 500\nFeatures: inn, market"
    expected_output2 = "Town: Dunharrow\nPopulation: 800\nFeatures: blacksmith, tavern"

    assert overview1.display_overview() == expected_output1, "First town overview should display the correct details."
    assert overview2.display_overview() == expected_output2, "Second town overview should display the correct details."