import pygame
from ui import Button

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_GRAY = (40, 40, 40)
GRAY = (128, 128, 128)
SKY_BLUE = (135, 206, 235)
DARK_BROWN = (101, 67, 33)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)
DARK_PURPLE = (75, 0, 130)
ORANGE = (255, 165, 0)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


class ShopScreen:
    def __init__(self, screen, total_coins, upgrades, shop_items):
        self.screen = screen
        self.total_coins = total_coins
        self.upgrades = upgrades
        self.shop_items = shop_items
        self.font = pygame.font.Font(None, 40)
        self.item_buttons = []
        self.setup_buttons()

    def setup_buttons(self):
        num_items = len(self.shop_items)
        items_per_row = 2
        
        button_width = 300
        button_height = 180
        
        x_padding = 40
        y_padding = 40
        
        start_x = (SCREEN_WIDTH - (items_per_row * button_width + (items_per_row - 1) * x_padding)) / 2
        start_y = 150
        
        row, col = 0, 0
        
        for item_id, item_data in self.shop_items.items():
            x = start_x + col * (button_width + x_padding)
            y = start_y + row * (button_height + y_padding)
            
            button = Button(
                x,
                y,
                button_width,
                button_height,
                "",
                DARK_GRAY,
                GRAY
            )
            
            self.item_buttons.append({
                'id': item_id,
                'button': button,
                'data': item_data
            })
            
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_text("Shop", 80, SCREEN_WIDTH / 2, 60, GOLD)
        self.draw_text(f"Total Coins: {self.total_coins}", 40, SCREEN_WIDTH / 2, 120, GOLD)

        for item in self.item_buttons:
            item_id = item['id']
            item_data = item['data']
            button = item['button']

            # Draw button background and border
            button.draw(self.screen, pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, GOLD, button.rect, 2)
            
            # Display item name, description, and price
            self.draw_text(item_data['name'], 36, button.rect.centerx, button.rect.y + 30)
            self.draw_text(item_data['description'], 24, button.rect.centerx, button.rect.y + 70)
            self.draw_text(f"Price: {item_data['price']}", 28, button.rect.centerx, button.rect.y + 110)

            if self.upgrades[item_id]:
                s = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
                s.fill((0, 0, 0, 128))
                self.screen.blit(s, button.rect.topleft)
                self.draw_text("Purchased", 36, button.rect.centerx, button.rect.centery, GREEN)
            else:
                 buy_button = Button(
                    button.rect.centerx - 50,
                    button.rect.y + 140,
                    100,
                    30,
                    "Buy",
                    GREEN,
                    PURPLE
                )
                 buy_button.draw(self.screen, pygame.mouse.get_pos())
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        for item in self.item_buttons:
            if not self.upgrades[item['id']]:
                buy_button_rect = pygame.Rect(
                    item['button'].rect.centerx - 50,
                    item['button'].rect.y + 140,
                    100,
                    30
                )
                if buy_button_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     if self.total_coins >= item['data']['price']:
                        return item['id']
        return None

    def draw_text(self, text, size, x, y, color=WHITE, align="center"):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = (x, y)
        elif align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "topright":
            text_rect.topright = (x, y)
        self.screen.blit(text_surface, text_rect)