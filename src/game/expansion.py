from app.inventory import Item

class ExpansionContent:
    def __init__(self):
        self.new_quests = []
        self.new_items = []

    def add_new_quest(self, quest_name):
        """Add a new quest from the expansion content."""
        self.new_quests.append(quest_name)

    def add_new_item(self, item_name):
        """Add a new item from the expansion content."""
        self.new_items.append(Item(name=item_name))

    def integrate_into_game(self, game_state):
        """Integrate the expansion content into the game state."""
        for quest in self.new_quests:
            game_state.quest_status[quest] = 'Not Started'
        for item in self.new_items:
            game_state.inventory.add_item(item)