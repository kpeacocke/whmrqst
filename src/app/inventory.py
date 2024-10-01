class Item:
    def __init__(self, name, quantity=1):
        self.name = name
        self.quantity = quantity

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        existing_item = self.get_item(item.name)
        if existing_item:
            existing_item.quantity += item.quantity
            return True
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item_name, quantity=1):
        item = self.get_item(item_name)
        if item:
            if item.quantity > quantity:
                item.quantity -= quantity
            else:
                self.items.remove(item)
            return True
        return False

    def get_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                return item
        return None