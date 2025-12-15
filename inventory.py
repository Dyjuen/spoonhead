import pygame
from ui import Button
from settings import *

TIER_COLORS = {
    "Common": GRAY,
    "Rare": BLUE,
    "Epic": PURPLE,
    "Legendary": GOLD
}

class InventoryScreen:
    def __init__(self, screen, selected_character_id, unlocked_guns, gun_data, character_data, equipped_gun_id):
        self.screen = screen
        self.selected_character_id = selected_character_id
        self.unlocked_guns = unlocked_guns
        self.gun_data = gun_data
        self.character_data = character_data
        self.equipped_gun_id = equipped_gun_id
        
        self.font = pygame.font.Font(PIXEL_FONT, 24)
        self.item_font = pygame.font.Font(PIXEL_FONT, 16)
        self.tier_font = pygame.font.Font(PIXEL_FONT, 12)

        self.back_button = Button(20, 20, 150, 50, "Back", RED, PURPLE)

        self.unlocked_characters = ['cyborg', 'biker', 'punk']  # All characters are selectable
        
        # Load images
        self.character_images = self._load_character_images()
        self.gun_images = self._load_gun_images()
        self.lock_icon = self._create_lock_icon()

        self.scroll_y = 0
        self.gun_grid_rects = {}

    def _load_character_images(self):
        images = {}
        for char_id, char_data in self.character_data.items():
            try:
                img = pygame.image.load(char_data['idle']).convert_alpha()
                images[char_id] = pygame.transform.scale(img, (80, 80))
            except pygame.error:
                img = pygame.Surface((80, 80), pygame.SRCALPHA)
                img.fill(BLUE)
                images[char_id] = img
        return images

    def _load_gun_images(self):
        images = {}
        for gun_id, gun_data in self.gun_data.items():
            try:
                img = pygame.image.load(gun_data['image_path']).convert_alpha()
                images[gun_id] = pygame.transform.scale(img, (60, 60))
            except pygame.error:
                img = pygame.Surface((60, 60), pygame.SRCALPHA)
                img.fill(GRAY)
                images[gun_id] = img
        return images
        
    def _create_lock_icon(self):
        icon = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.rect(icon, GOLD, (0, 15, 30, 25), border_radius=5)
        pygame.draw.circle(icon, GOLD, (15, 15), 15, 5, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(icon, BLACK, (15, 28), 5)
        return icon

    def update_data(self, selected_character_id, unlocked_guns, equipped_gun_id):
        self.selected_character_id = selected_character_id
        self.unlocked_guns = unlocked_guns
        self.equipped_gun_id = equipped_gun_id

    def draw(self):
        self.screen.fill(DARK_GRAY)
        mouse_pos = pygame.mouse.get_pos()

        # Title
        self.draw_text("Inventory", 36, SCREEN_WIDTH / 2, 50, WHITE)

        # Characters Section
        self.draw_text("Characters", 28, 250, 120, WHITE)
        char_y = 180
        for char_id, char_data in self.character_data.items():
            is_unlocked = char_id in self.unlocked_characters
            is_selected = char_id == self.selected_character_id
            
            char_rect = pygame.Rect(100, char_y, 300, 100)
            
            # Draw border if selected
            if is_selected:
                pygame.draw.rect(self.screen, GREEN, char_rect.inflate(6, 6), 3, border_radius=10)

            # Draw card
            pygame.draw.rect(self.screen, GRAY, char_rect, border_radius=10)
            
            # Image - use the single idle image
            char_img = self.character_images[char_id]
            self.screen.blit(char_img, (char_rect.x + 10, char_rect.y + 10))

            # Name
            self.draw_text(char_data['name'], 20, char_rect.x + 180, char_rect.y + 40, WHITE)

            # Locked overlay
            if not is_unlocked:
                overlay = pygame.Surface(char_rect.size, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, char_rect.topleft)
                self.screen.blit(self.lock_icon, (char_rect.centerx - 15, char_rect.centery - 20))
            
            char_y += 120

        # Guns Section
        self.draw_text("Weapons", 28, SCREEN_WIDTH / 2 + 300, 120, WHITE)
        
        # Grid layout
        cols = 5
        item_width, item_height = 120, 120
        gap = 20
        start_x = 550
        start_y = 180
        
        self.gun_grid_rects.clear()

        for i, (gun_id, gun_data) in enumerate(self.gun_data.items()):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (item_width + gap)
            y = start_y + row * (item_height + gap) - self.scroll_y

            if y + item_height < start_y or y > SCREEN_HEIGHT - 100:
                continue

            gun_rect = pygame.Rect(x, y, item_width, item_height)
            self.gun_grid_rects[gun_id] = gun_rect

            is_unlocked = gun_id in self.unlocked_guns
            is_equipped = gun_id == self.equipped_gun_id

            # Border for tier and selection
            tier_color = TIER_COLORS.get(gun_data['tier'], GRAY)
            border_color = GREEN if is_equipped else tier_color
            border_width = 4 if is_equipped else 2
            pygame.draw.rect(self.screen, border_color, gun_rect, border_width, border_radius=8)
            
            # Image
            gun_img = self.gun_images[gun_id]
            self.screen.blit(gun_img, (gun_rect.centerx - 30, gun_rect.y + 10))

            # Name
            self.draw_text(gun_data['name'], 14, gun_rect.centerx, gun_rect.y + 85, WHITE)

            # Tier
            self.draw_text(gun_data['tier'], 12, gun_rect.centerx, gun_rect.y + 105, tier_color)

            # Locked overlay
            if not is_unlocked:
                overlay = pygame.Surface(gun_rect.size, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, gun_rect.topleft)
                self.screen.blit(self.lock_icon, (gun_rect.centerx - 15, gun_rect.centery - 20))
        
        # Back button
        self.back_button.draw(self.screen, mouse_pos)
        pygame.display.flip()

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.back_button.is_clicked(event, mouse_pos):
            return 'back'
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Character selection
                char_y = 180
                for char_id in self.character_data:
                    if char_id in self.unlocked_characters:
                        char_rect = pygame.Rect(100, char_y, 300, 100)
                        if char_rect.collidepoint(mouse_pos):
                            return ('character_selected', char_id)
                    char_y += 120

                # Gun selection
                for gun_id, rect in self.gun_grid_rects.items():
                    if gun_id in self.unlocked_guns:
                        if rect.collidepoint(mouse_pos):
                            return ('gun_selected', gun_id)
            
            # Scrolling
            elif event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 30)
            elif event.button == 5:  # Scroll down
                # You might want to calculate a proper max_scroll value
                self.scroll_y += 30

        return None

    def draw_text(self, text, size, x, y, color):
        font = pygame.font.Font(PIXEL_FONT, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)