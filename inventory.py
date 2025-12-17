import pygame
from ui import Button
from settings import *
from sprites import SpriteSheet
import random

def get_scaled_size(original_size, max_size):
    """
    Calculates the new dimensions for an image to fit within a max_size box
    while preserving the aspect ratio.
    """
    original_width, original_height = original_size
    max_width, max_height = max_size

    if original_width == 0 or original_height == 0:
        return (0, 0)

    aspect_ratio = original_width / original_height

    # Calculate new dimensions based on aspect ratio
    new_width = max_width
    new_height = new_width / aspect_ratio
    
    if new_height > max_height:
        new_height = max_height
        new_width = new_height * aspect_ratio

    return (int(new_width), int(new_height))

TIER_COLORS = {
    "Common": GRAY,
    "Rare": BLUE,
    "Epic": PURPLE,
    "Legendary": GOLD
}

class InventoryScreen:
    def __init__(self, screen, selected_character_id, unlocked_guns, gun_data, character_data, equipped_gun_id, unlocked_characters):
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

        # Unlocked characters should be passed from Game, not hardcoded here
        self.unlocked_characters = unlocked_characters # Now a parameter
        
        # Load images
        self.character_animations = self._load_character_animations()
        self.gun_images = self._load_gun_images()
        self.lock_icon = self._create_lock_icon()

        self.scroll_y = 0
        self.gun_grid_rects = {}

    def _load_character_animations(self):
        animations = {}
        player_size = (80, 80) # Size for inventory display

        for char_id, char_data in self.character_data.items():
            animations[char_id] = {}
            # Load idle animation (from sprite sheet)
            try:
                sheet = SpriteSheet(char_data['idle'])
                # Assuming original sprite sheet frames are 48x48
                frames = sheet.get_animation_frames(48, 48) 
                animations[char_id]['idle'] = [pygame.transform.scale(frame, player_size) for frame in frames]
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load idle animation for {char_id}: {char_data['idle']}")
                placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                animations[char_id]['idle'] = [placeholder_frame] * 4 # Fallback

            # Load emote animations (single images)
            if 'emotes' in char_data:
                for i, emote_path in enumerate(char_data['emotes']):
                    emote_key = f'emote_{i}'
                    try:
                        img = pygame.image.load(emote_path).convert_alpha()
                        animations[char_id][emote_key] = [pygame.transform.scale(img, player_size)] # Single frame
                    except (pygame.error, FileNotFoundError):
                        print(f"Warning: Could not load emote animation for {char_id}: {emote_path}")
                        placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                        animations[char_id][emote_key] = [placeholder_frame]

        return animations

    def _load_gun_images(self):
        images = {}
        max_size = (80, 80) # Bounding box for gun images in inventory
        for gun_id, gun_data in self.gun_data.items():
            try:
                img = pygame.image.load(gun_data['image_path']).convert_alpha()
                original_size = gun_data.get('size', (img.get_width(), img.get_height()))
                
                scaled_size = get_scaled_size(original_size, max_size)
                images[gun_id] = pygame.transform.scale(img, scaled_size)

            except pygame.error:
                original_size = gun_data.get('size', max_size)
                scaled_size = get_scaled_size(original_size, max_size)
                
                img = pygame.Surface(scaled_size, pygame.SRCALPHA)
                img.fill(GRAY)
                images[gun_id] = img
        return images
        
    def _create_lock_icon(self):
        icon = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.rect(icon, GOLD, (0, 15, 30, 25), border_radius=5)
        pygame.draw.circle(icon, GOLD, (15, 15), 15, 5, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(icon, BLACK, (15, 28), 5)
        return icon

    def update_data(self, selected_character_id, unlocked_guns, equipped_gun_id, unlocked_characters):
        self.selected_character_id = selected_character_id
        self.unlocked_guns = unlocked_guns
        self.equipped_gun_id = equipped_gun_id
        self.unlocked_characters = unlocked_characters # Update unlocked characters

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
            
            # Image - Animated character preview (always idle animation)
            char_animations_dict = self.character_animations[char_id] # This is a dict of animation lists
            
            current_anim_key = 'idle' # Always play idle animation
            current_animation_frames = char_animations_dict.get(current_anim_key, char_animations_dict['idle'])
            frame_index = (pygame.time.get_ticks() // 150) % len(current_animation_frames) # Cycle faster
            char_img = current_animation_frames[frame_index]
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
            img_rect = gun_img.get_rect(center=(gun_rect.centerx, gun_rect.y + 40)) # Center in the top part
            self.screen.blit(gun_img, img_rect)

            # Name
            self.draw_text(gun_data['name'], 8, gun_rect.centerx, gun_rect.y + 85, WHITE)

            # Tier
            self.draw_text(gun_data['tier'], 10, gun_rect.centerx, gun_rect.y + 105, tier_color)

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
                    # Only allow selection of unlocked characters
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