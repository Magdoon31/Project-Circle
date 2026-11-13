# THE STATS PAGE (13.11) - the map's menu (ESC) -> Stats: four cards side by side (General, Fights, Gold & items,
# Minigames & more), each a list of "name ...... number" for this save. The numbers come from Game (rows()).

import pygame

from game.menu import fancy_text as FANCY

CARDS_TOP, CARDS_H = 0.2, 0.52        # shares of the screen's height
CARDS_W, GAP = 0.215, 0.015           # a card's width and the gap, shares of the screen's width
PANEL, PANEL_EDGE = (16, 10, 26, 215), (120, 96, 160)
TEXT, MUTED = (236, 228, 214), (170, 150, 200)
COLOURS = [(150, 210, 120), (240, 130, 140), (250, 210, 120), (160, 200, 250)]


class StatsScreen:
    def __init__(self, screen, cards):
        """cards: [(title, [(label, value text)])]."""
        self.screen, self.cards = screen, cards

    def draw(self):
        w, h = self.screen.get_size()
        total = len(self.cards) * CARDS_W + (len(self.cards) - 1) * GAP
        left = (1 - total) / 2
        for n, (title, rows) in enumerate(self.cards):
            rect = pygame.Rect(int(w * (left + n * (CARDS_W + GAP))), int(h * CARDS_TOP), int(w * CARDS_W), int(h * CARDS_H))
            self.draw_card(rect, title, rows, COLOURS[n % len(COLOURS)])

    def draw_card(self, rect, title, rows, colour):
        h = self.screen.get_height()
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, PANEL, panel.get_rect(), 0, 18)
        self.screen.blit(panel, rect)
        pygame.draw.rect(self.screen, PANEL_EDGE, rect, 2, 18)
        pad = int(h * 0.02)
        k = min(h, rect.width * 4.2)                          # (fonts follow the card's width on narrow screens)
        head = fitted(FANCY.font(int(k * 0.028)), title.upper(), colour, rect.width - 2 * pad)
        self.screen.blit(head, (rect.left + pad, rect.top + pad))
        y = rect.top + pad + head.get_height() + int(h * 0.006)
        pygame.draw.line(self.screen, colour, (rect.left + pad, y), (rect.right - pad, y), 1)
        y += int(h * 0.016)
        label_font, value_font = FANCY.font(int(k * 0.021)), FANCY.font(int(k * 0.023))
        step = int(h * 0.043)
        for label, value in rows:
            number = value_font.render(value, True, TEXT)
            name = fitted(label_font, label, MUTED, rect.width - 2 * pad - number.get_width() - 12)
            self.screen.blit(name, (rect.left + pad, y))
            self.screen.blit(number, number.get_rect(topright=(rect.right - pad, y)))
            dots_from, dots_to = rect.left + pad + name.get_width() + 8, rect.right - pad - number.get_width() - 8
            for x in range(dots_from, dots_to, 8):                    # a dotted leader between them
                pygame.draw.circle(self.screen, (70, 58, 96), (x, y + name.get_height() - 4), 1)
            y += step


def fitted(font, text, colour, width):
    """The text rendered, squeezed to `width` if it is wider."""
    picture = font.render(text, True, colour)
    if picture.get_width() > width:
        picture = pygame.transform.smoothscale(picture, (width, picture.get_height()))
    return picture
