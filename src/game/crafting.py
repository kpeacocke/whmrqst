from app.inventory import Item


class CraftingSystem:
    def __init__(self, recipes):
        self.recipes = recipes

    def craft(self, inventory, recipe_name):
        """Craft an item based on the recipe if the required materials are available."""
        if recipe_name not in self.recipes:
            return None

        recipe = self.recipes[recipe_name]
        if inventory.has_items(recipe["materials"]):
            inventory.remove_items(recipe["materials"])
            crafted_item = Item(name=recipe["result"], quantity=recipe.get("quantity", 1))
            inventory.add_item(crafted_item)
            return crafted_item
        return None