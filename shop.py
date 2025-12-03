import pygame
from ui import Button
from settings import PIXEL_FONT

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
        self.font = pygame.font.Font(PIXEL_FONT, 40)
        self.item_buttons = []
        self.scroll_y = 0
        self.setup_buttons()

    def setup_buttons(self):
        self.item_buttons = []
        start_x = 150
        start_y = 200
        y_offset = 0
        
        for item_id, item_data in self.shop_items.items():
            x = start_x
            y = start_y + y_offset
            
            # Main item button
            item_button = Button(x, y, SCREEN_WIDTH - 300, 120, "", DARK_GRAY, GRAY)
            
            # Buy button
            buy_button = Button(x + item_button.rect.width - 120, y + 75, 100, 30, "Buy", GREEN, DARK_PURPLE)

            self.item_buttons.append({
                'id': item_id,
                'button': item_button,
                'buy_button': buy_button,
                'data': item_data,
                'original_y': y
            })
            
            y_offset += 140 # spacing between items

    def draw(self):
        self.draw_text("Shop", 60, SCREEN_WIDTH / 2, 60, GOLD)
        self.draw_text(f"Total Coins: {self.total_coins}", 30, SCREEN_WIDTH / 2, 120, GOLD)

        content_height = len(self.item_buttons) * 140
        mouse_pos = pygame.mouse.get_pos()
        
        for item in self.item_buttons:
            item_id = item['id']
            item_data = item['data']
            button = item['button']
            buy_button = item['buy_button']
            current_level = self.upgrades.get(item_id, 0)
            max_level = item_data['max_level']

            # Adjust y-position for scrolling for all buttons
            button.rect.y = item['original_y'] - self.scroll_y
            buy_button.rect.y = item['original_y'] - self.scroll_y + 75


            # Only draw if visible
            if button.rect.bottom > 150 and button.rect.top < SCREEN_HEIGHT:
                                button.draw(self.screen, mouse_pos)                pygame.draw.rect(self.screen, GOLD, button.rect, 2)
                
                # Display item name, description and level
                self.draw_text(item_data['name'], 22, button.rect.x + 150, button.rect.y + 30,align='center')
                self.draw_text(item_data['description'], 16, button.rect.x + 250, button.rect.y + 60,align='center')
                if max_level > 1:
                    self.draw_text(f"Level: {current_level}/{max_level}", 16, button.rect.x + 150, button.rect.y + 90,align='center')

                if current_level >= max_level:
                    if max_level == 1:
                        self.draw_text("Purchased", 20, buy_button.rect.centerx, buy_button.rect.centery, GREEN)
                    else:
                        self.draw_text("Max Level", 24, buy_button.rect.centerx, buy_button.rect.centery, GREEN)
                else:
                    price = item_data['prices'][current_level]
                    can_afford = self.total_coins >= price
                    
                    buy_button.text = f"Buy ({price})"
                    buy_button.color = GREEN if can_afford else GRAY
                    buy_button.hover_color = ORANGE if can_afford else GRAY
                    
                    buy_button.draw(self.screen, mouse_pos)

        # Draw scrollbar
        if content_height > SCREEN_HEIGHT - 200:
            scrollbar_area_height = SCREEN_HEIGHT - 220
            scrollbar_area = pygame.Rect(SCREEN_WIDTH - 25, 170, 20, scrollbar_area_height)
            pygame.draw.rect(self.screen, DARK_GRAY, scrollbar_area)

            # Recalculate based on actual rendered content area, not just number of items
            # The total height of all items
            total_content_height = len(self.item_buttons) * 140 
            
            # The visible area height
            visible_height = SCREEN_HEIGHT - 200 
            
            if total_content_height > visible_height:
                handle_height = visible_height * (visible_height / total_content_height)
                handle_height = max(handle_height, 20) # Minimum handle height

                # Calculate the scroll ratio (0.0 to 1.0)
                max_scroll = total_content_height - visible_height
                scroll_ratio = self.scroll_y / max_scroll if max_scroll > 0 else 0
                
                handle_y = scrollbar_area.y + scroll_ratio * (scrollbar_area.height - handle_height)

                scrollbar_handle = pygame.Rect(SCREEN_WIDTH - 25, handle_y, 20, handle_height)
                pygame.draw.rect(self.screen, GRAY, scrollbar_handle)


    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 30)
            elif event.button == 5:  # Scroll down
                content_height = len(self.item_buttons) * 140
                max_scroll = max(0, content_height - (SCREEN_HEIGHT - 200))
                self.scroll_y = min(max_scroll, self.scroll_y + 30)

        for item in self.item_buttons:
            item_id = item['id']
            item_data = item['data']
            buy_button = item['buy_button']
            current_level = self.upgrades.get(item_id, 0)
            max_level = item_data['max_level']

            if current_level < max_level:
                price = item_data['prices'][current_level]
                if self.total_coins >= price and buy_button.is_clicked(event, mouse_pos):
                    return item_id
        return None

    def draw_text(self, text, size, x, y, color=WHITE, align="center"):
        font = pygame.font.Font(PIXEL_FONT, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = (x, y)
        elif align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "topright":
            text_rect.topright = (x, y)
        self.screen.blit(text_surface, text_rect)