import pygame
from ui import Button
from settings import *
from sprites import SpriteSheet
import random

TIER_COLORS = {
    "Common": GRAY,
    "Rare": BLUE,
    "Epic": PURPLE,
    "Legendary": GOLD
}

class InventoryScreen:
    def __init__(self, screen, selected_characters, unlocked_guns, gun_data, character_data, equipped_guns, unlocked_characters, connected_players=[0]):
        self.screen = screen
        self.selected_characters = selected_characters # Dict: {0: 'id', 1: 'id'}
        self.unlocked_guns = unlocked_guns
        self.gun_data = gun_data
        self.character_data = character_data
        self.equipped_guns = equipped_guns # Dict: {0: 'id', 1: 'id'}
        
        self.font = pygame.font.Font(PIXEL_FONT, 24)
        self.item_font = pygame.font.Font(PIXEL_FONT, 16)
        self.tier_font = pygame.font.Font(PIXEL_FONT, 12)

        self.back_button = Button(20, 20, 150, 50, "Back", RED, PURPLE)
        self.player_toggle_button = Button(SCREEN_WIDTH - 170, 20, 150, 50, "Edit: P1", GREEN, DARK_GRAY)

        self.unlocked_characters = unlocked_characters
        self.connected_players = connected_players
        self.active_player_idx = 0
        
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

    def update_data(self, selected_characters, unlocked_guns, equipped_guns, unlocked_characters, connected_players):
        self.selected_characters = selected_characters
        self.unlocked_guns = unlocked_guns
        self.equipped_guns = equipped_guns
        self.unlocked_characters = unlocked_characters
        self.connected_players = connected_players
        # Ensure active player is valid
        if self.active_player_idx not in self.connected_players:
            self.active_player_idx = self.connected_players[0]
        
        # Update button text/color
        self._update_toggle_button()

    def _update_toggle_button(self):
        self.player_toggle_button.text = f"Edit: P{self.active_player_idx + 1}"
        self.player_toggle_button.bg_color = GREEN if self.active_player_idx == 0 else BLUE

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
            
            char_rect = pygame.Rect(100, char_y, 300, 100)
            
            # Draw card
            pygame.draw.rect(self.screen, GRAY, char_rect, border_radius=10)

            # Selection Borders
            # P1 = Green, P2 = Blue
            p1_selected = self.selected_characters.get(0) == char_id
            p2_selected = self.selected_characters.get(1) == char_id

            if p1_selected and p2_selected:
                 # Split border? Or dashed? Let's do double border.
                 pygame.draw.rect(self.screen, GREEN, char_rect.inflate(10, 10), 3, border_radius=12)
                 pygame.draw.rect(self.screen, BLUE, char_rect.inflate(6, 6), 3, border_radius=10)
                 self.draw_text("P1 & P2", 12, char_rect.right + 30, char_rect.centery, WHITE)
            elif p1_selected:
                pygame.draw.rect(self.screen, GREEN, char_rect.inflate(6, 6), 3, border_radius=10)
                self.draw_text("P1", 14, char_rect.right + 20, char_rect.centery, GREEN)
            elif p2_selected:
                pygame.draw.rect(self.screen, BLUE, char_rect.inflate(6, 6), 3, border_radius=10)
                self.draw_text("P2", 14, char_rect.right + 20, char_rect.centery, BLUE)
            
            # Image - Animated character preview
            char_animations_dict = self.character_animations[char_id]
            
            current_anim_key = 'idle'
            current_animation_frames = char_animations_dict.get(current_anim_key, char_animations_dict['idle'])
            frame_index = (pygame.time.get_ticks() // 150) % len(current_animation_frames)
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
        self.draw_text("Weapons (Shared)", 28, SCREEN_WIDTH / 2 + 300, 120, WHITE)
        
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
            
            p1_equipped = self.equipped_guns.get(0) == gun_id
            p2_equipped = self.equipped_guns.get(1) == gun_id

            # Border for tier and selection
            tier_color = TIER_COLORS.get(gun_data['tier'], GRAY)
            
            if p1_equipped and p2_equipped:
                 pygame.draw.rect(self.screen, GREEN, gun_rect.inflate(8, 8), 3, border_radius=10)
                 pygame.draw.rect(self.screen, BLUE, gun_rect.inflate(4, 4), 3, border_radius=8)
                 # self.draw_text("P1/P2", 10, gun_rect.centerx, gun_rect.top - 10, WHITE)
            elif p1_equipped:
                pygame.draw.rect(self.screen, GREEN, gun_rect, 4, border_radius=8)
                # self.draw_text("P1", 10, gun_rect.centerx, gun_rect.top - 10, GREEN)
            elif p2_equipped:
                pygame.draw.rect(self.screen, BLUE, gun_rect, 4, border_radius=8)
                # self.draw_text("P2", 10, gun_rect.centerx, gun_rect.top - 10, BLUE)
            else:
                pygame.draw.rect(self.screen, tier_color, gun_rect, 2, border_radius=8)
            
            # Image
            gun_img = self.gun_images[gun_id]
            self.screen.blit(gun_img, (gun_rect.centerx - 30, gun_rect.y + 10))

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
        
        # Draw toggle button if multiple players possible (even if not joined yet? No, only if connected)
        # Actually, let's allow toggling if P2 is connected.
        if len(self.connected_players) > 1:
            self.player_toggle_button.draw(self.screen, mouse_pos)
            
        pygame.display.flip()

    def handle_event(self, event):
        # Default mouse handling
        mouse_pos = pygame.mouse.get_pos()
        
        if self.back_button.is_clicked(event, mouse_pos):
            return 'back'
            
        if len(self.connected_players) > 1 and self.player_toggle_button.is_clicked(event, mouse_pos):
            # Cycle through connected players
            current_idx = self.connected_players.index(self.active_player_idx)
            next_idx = (current_idx + 1) % len(self.connected_players)
            self.active_player_idx = self.connected_players[next_idx]
            self._update_toggle_button()
            return None # Consumed
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Character selection
                char_y = 180
                for char_id in self.character_data:
                    # Only allow selection of unlocked characters
                    if char_id in self.unlocked_characters:
                        char_rect = pygame.Rect(100, char_y, 300, 100)
                        if char_rect.collidepoint(mouse_pos):
                            return ('character_selected', self.active_player_idx, char_id) 
                    char_y += 120

                # Gun selection
                for gun_id, rect in self.gun_grid_rects.items():
                    if gun_id in self.unlocked_guns:
                        if rect.collidepoint(mouse_pos):
                            return ('gun_selected', self.active_player_idx, gun_id) 
            
            # Scrolling
            elif event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 30)
            elif event.button == 5:  # Scroll down
                # You might want to calculate a proper max_scroll value
                self.scroll_y += 30

        return None
    
    def handle_input(self, actions, player_index):
        # Handle controller/keyboard navigation for inventory (simplified for now)
        # This function can be called by main loop for P1 and P2 actions
        # For now, we will just rely on mouse for P1, and maybe add simple P2 cycle later
        # Or, P2 can cycle with 'jump' to select next char?
        
        if actions.get('shoot'): # Use Shoot button to cycle characters
             # Logic to cycle next unlocked character for this player
             pass
        
        return None

    def draw_text(self, text, size, x, y, color):
        font = pygame.font.Font(PIXEL_FONT, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)