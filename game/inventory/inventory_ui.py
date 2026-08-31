import pygame

class Inventory_ui:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.selected_item = None

    def draw(self):
        self.screen.fill((200, 200, 120))

    def handle_click(self, pos):
        
