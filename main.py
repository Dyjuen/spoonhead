import pygame
import os
import json
import random
import subprocess
import sys
from settings import *
from controller import ControllerManager
from sprites import Player, Boss, Projectile, BossProjectile, Platform, MovingPlatform, Coin, Enemy, BossGate, PowerUpBox, PowerUp, EnemyProjectile
from ui import Button
from level_data import ALL_LEVELS
from shop_data import SHOP_ITEMS
from shop import ShopScreen
from gun_data import GUN_DATA
from inventory import InventoryScreen, TIER_COLORS # Import TIER_COLORS
from benchmark import Benchmark
from parallax import Parallax
from gacha import play_gacha_animation

SAVE_FILE = 'save.json'

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

def collide_hitbox(sprite1, sprite2):
    return sprite1.hitbox.colliderect(sprite2.hitbox)

class Game:
    """Main game class with a multi-level structure and persistence."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        Projectile.load_images()
        pygame.display.set_caption("Spoonhead")
        self.clock = pygame.time.Clock()
        self.running = True # Initialize self.running
        self.game_state = 'home_screen'
        self.blink_timer = 0
        self.show_start_text = True

        # Game settings
        self.volume = 1.0
        self.fullscreen = False
        self.paused = False
        self.walking_sound_playing = False
        self.u_pressed = False
        self._mixer_was_initialized = True # Assume initialized at start
        self.gacha_gun_display_images = {} # For displaying gun in gacha animation
        self._mixer_was_initialized = True # Assume initialized at start

        self.screen_shake_duration = 0
        self.screen_shake_intensity = 0
        self.screen_shake_start_time = 0

        self.unlocked_levels = 1
        self.total_coins = 0
        self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
        self.current_level = 1 # Change from 0 to 1
        
        # Multiplayer Data
        self.controller_manager = ControllerManager()
        self.connected_players = [0] # List of active player indices (0 for P1, 1 for P2)
        
        self.unlocked_characters = ['cyborg'] 
        self.selected_characters = {0: 'cyborg', 1: 'biker'} # Default for P1 and P2
        self.unlocked_guns = ['pistol_1'] 
        self.equipped_guns = {0: 'pistol_1', 1: 'pistol_1'} # Default for P1 and P2
        
        self.load_game_data()

        self.camera_x = 0
        self.players = [] # List to hold Player objects
        self.player = None # Keep for backward compatibility/single player logic ease
        
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.boss_gate_group = pygame.sprite.Group()
        self.power_up_boxes = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.boss = None

        # Level selection
        self.scroll_x = 0
        self.level_cards = []
        
        self.shop_screen = ShopScreen(self.screen, self.total_coins, self.upgrades, SHOP_ITEMS)
        self.inventory_screen = InventoryScreen(self.screen, self.selected_characters, self.unlocked_guns, GUN_DATA, CHARACTER_DATA, self.equipped_guns, self.unlocked_characters, self.connected_players)
        self.benchmark = Benchmark(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.parallax = Parallax(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.load_assets()
        self.apply_settings()

        # Start theme music
        pygame.mixer.music.load(THEME_MUSIC)
        pygame.mixer.music.play(-1)

    def load_game_data(self):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                self.unlocked_levels = data.get('unlocked_levels', 1)
                self.total_coins = data.get('total_coins', 0)
                self.volume = data.get('volume', 1.0)
                self.fullscreen = data.get('fullscreen', False)
                loaded_upgrades = data.get('upgrades', {})
                for item_id in SHOP_ITEMS:
                    if item_id in loaded_upgrades:
                        self.upgrades[item_id] = loaded_upgrades[item_id]
                
                # Load unlocked characters and guns
                self.unlocked_characters = data.get('unlocked_characters', ['cyborg'])
                
                # Load selected character for P1 (P2 defaults to Biker or saved P1 preference?)
                # For simplicity, load P1 from save, P2 defaults to Biker unless changed in session
                p1_char = data.get('selected_character', 'cyborg')
                self.selected_characters[0] = p1_char if p1_char in self.unlocked_characters else 'cyborg'
                
                self.unlocked_guns = data.get('unlocked_guns', ['pistol_1'])
                p1_gun = data.get('equipped_gun_id', 'pistol_1')
                self.equipped_guns[0] = p1_gun if p1_gun in self.unlocked_guns else 'pistol_1'
                
                # Ensure P2 has valid defaults if unlocked
                if self.selected_characters[1] not in self.unlocked_characters:
                    self.selected_characters[1] = 'cyborg' # Fallback

        except (FileNotFoundError, json.JSONDecodeError):
            self.unlocked_levels = 1
            self.total_coins = 0
            self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
            self.current_level = 1
            self.unlocked_characters = ['cyborg']
            self.selected_characters = {0: 'cyborg', 1: 'biker'}
            self.unlocked_guns = ['pistol_1']
            self.equipped_guns = {0: 'pistol_1', 1: 'pistol_1'}
            self.volume = 1.0
            self.fullscreen = False


    def save_game_data(self):
        data = {
            'unlocked_levels': self.unlocked_levels,
            'total_coins': self.total_coins,
            'upgrades': self.upgrades,
            'volume': self.volume,
            'fullscreen': self.fullscreen,
            'unlocked_characters': self.unlocked_characters,
            'selected_character': self.selected_characters[0], # Save P1 selection
            'unlocked_guns': self.unlocked_guns,
            'equipped_gun_id': self.equipped_guns[0] # Save P1 selection
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)

    def apply_settings(self):
        pygame.mixer.music.set_volume(self.volume)
        if self.sfx:
            for sound in self.sfx.values():
                sound.set_volume(self.volume)

        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

        # After changing display mode, mixer might be uninitialized.
        # Re-initialize only if it's not already initialized.
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            self.load_assets()  # Reload sounds to ensure they are available

        pygame.mixer.music.set_volume(self.volume)  # Re-apply volume settings
        if self.game_state == 'platformer':
            pygame.mixer.music.load(LEVEL_MUSIC)
            pygame.mixer.music.play(-1)
        elif self.game_state == 'boss_fight':
            pygame.mixer.music.load(BOSS_THEME)
            pygame.mixer.music.play(-1)
        elif self.game_state in ['home_screen', 'level_selection', 'shop_screen', 'inventory', 'settings']:
            pygame.mixer.music.load(THEME_MUSIC)
            pygame.mixer.music.play(-1)

    def load_assets(self):
        try:
            self.menu_bg_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Background", "menu.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.sfx = {
                'default_shot': pygame.mixer.Sound(DEFAULT_SHOT_SOUND),
                'spread_shot': pygame.mixer.Sound(SPREAD_SHOT_SOUND),
                'burst_shot': pygame.mixer.Sound(BURST_SHOT_SOUND),
                'walk': pygame.mixer.Sound(WALK_SOUND),
                'death': pygame.mixer.Sound(DEATH_SOUND),
                'jump': pygame.mixer.Sound(JUMP_SOUND),
                'landing': pygame.mixer.Sound(LANDING_SOUND),
                'coin': pygame.mixer.Sound(COIN_SOUND),
                'victory': pygame.mixer.Sound(VICTORY_SOUND),
                'explosion': pygame.mixer.Sound("assets/audio/burst.mp3"), # Placeholder for explosion sound
            }
            self.death_sound = self.sfx['death'] # Keep separate reference for existing logic
        except pygame.error as e:
            self.sfx = {}
            self.death_sound = None
        self.start_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Start Game", BLUE, PURPLE)
        self.settings_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Settings", GRAY, PURPLE)
        self.quit_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 90, 200, 50, "Quit Game", RED, PURPLE)
        
        # Benchmark Button
        self.benchmark_button = Button(20, SCREEN_HEIGHT - 70, 220, 50, "Benchmark Test", DARK_GRAY, BLUE, font_size=12)
        
        self.level_cards = []

        self.shop_button = Button(SCREEN_WIDTH - 170, 20, 150, 50, "Shop", GOLD, PURPLE, font_size=16)
        self.inventory_button = Button(SCREEN_WIDTH - 170, 90, 150, 50, "Inventory", GOLD, PURPLE, font_size=12)
        self.back_button = Button(20, 20, 150, 50, "Back", RED, PURPLE)
        self.level_select_button = Button(SCREEN_WIDTH - 60, 20, 40, 40, "X", RED, DARK_GRAY)


        # Settings screen buttons
        self.volume_down_button = Button(SCREEN_WIDTH/2 - 150, 275, 50, 50, "-", RED, PURPLE)
        self.volume_up_button = Button(SCREEN_WIDTH/2 + 100, 275, 50, 50, "+", GREEN, PURPLE)
        self.fullscreen_button = Button(SCREEN_WIDTH/2 - 150, 350, 300, 50, "Toggle Fullscreen", BLUE, PURPLE)

        # Pause menu buttons
        self.resume_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 120, 200, 50, "Resume", BLUE, PURPLE)
        self.settings_button_ingame = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Settings", GRAY, PURPLE)
        self.main_menu_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Main Menu", RED, PURPLE)
        self.exit_button_ingame = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 90, 200, 50, "Exit Game", DARK_GRAY, PURPLE)
        
        
        # Load gacha gun display images
        for gun_id, gun_info in GUN_DATA.items():
            try:
                img = pygame.image.load(gun_info['image_path']).convert_alpha()
                original_size = gun_info.get('size')
                if original_size:
                    scaled_size = get_scaled_size(original_size, (100, 100))
                    self.gacha_gun_display_images[gun_id] = pygame.transform.scale(img, scaled_size)
                else:
                    # Fallback for guns without size info, scale to a default
                    self.gacha_gun_display_images[gun_id] = pygame.transform.scale(img, (100, 100))

            except pygame.error:
                original_size = gun_info.get('size')
                if original_size:
                    scaled_size = get_scaled_size(original_size, (100, 100))
                    self.gacha_gun_display_images[gun_id] = pygame.Surface(scaled_size, pygame.SRCALPHA)
                else:
                    self.gacha_gun_display_images[gun_id] = pygame.Surface((100, 100), pygame.SRCALPHA)
                
                self.gacha_gun_display_images[gun_id].fill(GRAY)

        self.gacha_font = pygame.font.Font(PIXEL_FONT, 30)

    def init_level(self, level_number):
        self.current_level = level_number
        level_data = ALL_LEVELS[level_number]
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.boss_gate_group = pygame.sprite.Group()
        self.power_up_boxes = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        
        # Player
        self.player = Player(100, 400, self, upgrades=self.upgrades, character_id=self.selected_character, equipped_gun_id=self.equipped_gun_id, upgrades_data=self.upgrades)
        
        # Level Objects
        for p_data in level_data["platforms"]:
            self.platforms.add(Platform(*p_data))
        for p_data in level_data["moving_platforms"]:
            p = MovingPlatform(*p_data)
            self.platforms.add(p)
            self.moving_platforms.add(p)
        for c_data in level_data["coins"]:
            self.coins.add(Coin(*c_data))
        for e_data in level_data["enemies"]:
            self.enemies.add(Enemy(player=self.player, **e_data))
        for b_data in level_data.get("power_up_boxes", []):
            self.power_up_boxes.add(PowerUpBox(*b_data))
        
        self.boss_gate = BossGate(level_data["boss_gate_x"], 460)
        self.boss_gate_group.add(self.boss_gate)
        
        # Add all sprites to the main rendering group
        self.all_sprites.add(
            self.player, 
            self.platforms, 
            self.coins, 
            self.enemies, 
            self.power_up_boxes, 
            self.boss_gate
        )
        
        self.boss = None
        self.game_state = 'platformer'
        self.camera_x = 0
        
        pygame.mixer.music.stop()
        pygame.mixer.music.load(LEVEL_MUSIC)
        pygame.mixer.music.play(-1)

    def init_boss_fight(self):
        self.game_state = 'boss_fight'
        level_data = ALL_LEVELS[self.current_level]
        boss_data = level_data["boss"].copy()

        # Remove conflicting positional arguments before unpacking
        boss_data.pop('x', None)
        boss_data.pop('y', None)

        self.all_sprites.empty() # Clear all old sprites
        self.platforms.empty(); self.coins.empty(); self.enemies.empty(); self.boss_gate_group.empty()
        
        self.player.rect.center = (200, 400)
        self.player.hitbox.center = (200, 400)
        self.player.vy = 0
        self.player.on_ground = True
        self.all_sprites.add(self.player)
        self.camera_x = 0
        
        ground = Platform(0, 500, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground); self.platforms.add(ground)
        
        self.boss = Boss(x=SCREEN_WIDTH * 0.75, y=SCREEN_HEIGHT / 2, game=self, **boss_data)
        self.all_sprites.add(self.boss); self.boss_group.add(self.boss)

        pygame.mixer.music.stop()
        pygame.mixer.music.load(BOSS_THEME)
        pygame.mixer.music.play(-1)

    def draw_text(self, text, size, x, y, color=WHITE, align="center"):
        font = pygame.font.Font(PIXEL_FONT, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def _play_sfx(self, sfx_name, loops=0):
        if self.sfx.get(sfx_name):
            sfx_object = self.sfx[sfx_name]
            channel = pygame.mixer.find_channel(True) 
            if channel:
                channel.set_volume(self.volume)
                channel.play(sfx_object, loops)

    def start_screen_shake(self, duration, intensity):
        self.screen_shake_duration = duration
        self.screen_shake_intensity = intensity
        self.screen_shake_start_time = pygame.time.get_ticks()

    def buy_gun_crate(self):
        crate_cost = 500
        if self.total_coins >= crate_cost:
            self.total_coins -= crate_cost
            pygame.mixer.music.pause()

            rarity_weights = { 'Common': 0.6, 'Rare': 0.25, 'Epic': 0.1, 'Legendary': 0.05 }
            guns_by_tier = {tier: [] for tier in rarity_weights}
            for gun_id, gun_data in GUN_DATA.items():
                guns_by_tier[gun_data['tier']].append(gun_id)

            chosen_tier = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()), k=1)[0]
            
            if guns_by_tier[chosen_tier]:
                unlocked_gun_id = random.choice(guns_by_tier[chosen_tier])
                gun_data = GUN_DATA[unlocked_gun_id]
                
                is_duplicate = unlocked_gun_id in self.unlocked_guns
                if is_duplicate:
                    refund = crate_cost // 2
                    self.total_coins += refund
                else:
                    self.unlocked_guns.append(unlocked_gun_id)

                gacha_result = {
                    'gun_id': unlocked_gun_id,
                    'is_duplicate': is_duplicate,
                    'tier': chosen_tier,
                    'name': gun_data['name']
                }

                # Call the new blocking animation function
                play_gacha_animation(self.screen, gacha_result, self.gacha_gun_display_images, self.gacha_font)

                # After animation, update game state
                self.inventory_screen.update_data(self.selected_character, self.unlocked_guns, self.equipped_gun_id, self.unlocked_characters)
                self.save_game_data()
                self.shop_screen.total_coins = self.total_coins # Explicitly update shop UI coins
            
            pygame.mixer.music.unpause()
        else:
            # Not enough coins
            pass

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check for P2 join input anytime we are in menus where joining makes sense
        if self.game_state == 'level_selection':
            if 1 not in self.connected_players and self.controller_manager.has_p2_device():
                p2_controller = self.controller_manager.get_p2_controller()
                if p2_controller:
                    actions = p2_controller.get_actions()
                    if actions.get('join'):
                        self.connected_players.append(1)
                        self._play_sfx('coin') 
                        print("Player 2 Joined!")

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                    self.save_game_data()
                    self.running = False
                    if pygame.mixer.get_init():
                        pygame.mixer.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.game_state in ['platformer', 'boss_fight']:
                        self.paused = not self.paused
                    
                    if event.key == pygame.K_F3:
                        self.benchmark.toggle()

            if self.paused:
                if self.resume_button.is_clicked(event, mouse_pos):
                    self.paused = False
                elif self.settings_button_ingame.is_clicked(event, mouse_pos):
                    self.game_state = 'settings_ingame'
                    self.paused = False
                elif self.main_menu_button.is_clicked(event, mouse_pos):
                    self.paused = False
                    # self.total_coins += self.player.coins # Removed
                    self.save_game_data()
                    self.game_state = 'home_screen'
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(THEME_MUSIC)
                    pygame.mixer.music.play(-1)
                elif self.exit_button_ingame.is_clicked(event, mouse_pos):
                    self.save_game_data()
                    self.running = False
                return # Don't process other events when paused
            
            if self.game_state == 'settings_ingame':
                if self.back_button.is_clicked(event, mouse_pos):
                    self.game_state = 'platformer' # To return to the paused state, we set it back to platformer and then pause it
                    self.paused = True
                
                if self.volume_down_button.is_clicked(event, mouse_pos):
                    self.volume = max(0.0, round(self.volume - 0.1, 1))
                    self.apply_settings()
                    self.save_game_data()

                    if self.volume_up_button.is_clicked(event, mouse_pos):
                        self.volume = min(1.0, round(self.volume + 0.1, 1))
                        self.apply_settings()
                        self.save_game_data()
                    
                    if self.fullscreen_button.is_clicked(event, mouse_pos):
                        self.fullscreen = not self.fullscreen
                        self.apply_settings()
                        self.save_game_data()
                    return

                if self.game_state in ['platformer', 'boss_fight'] and self.level_select_button.is_clicked(event, mouse_pos):
                    self.save_game_data()
                    self.game_state = 'level_selection'
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(THEME_MUSIC)
                    pygame.mixer.music.play(-1)
                    return

                if self.game_state == 'victory':
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: 
                        self.all_sprites.empty()
                        self.platforms.empty()
                        self.moving_platforms.empty()
                        self.coins.empty()
                        self.enemies.empty()
                        self.projectiles.empty()
                        self.enemy_projectiles.empty()
                        self.boss_projectiles.empty()
                        self.boss_group.empty()
                        self.boss_gate_group.empty()
                        self.power_up_boxes.empty()
                        self.power_ups.empty()

                        self.players = [] 
                        self.player = None
                        self.boss = None
                        self.camera_x = 0
                        self.screen_shake_duration = 0
                        self.screen_shake_intensity = 0

                        self.game_state = 'level_selection'
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(THEME_MUSIC)
                        pygame.mixer.music.play(-1)
                elif self.game_state == 'game_over':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.init_level(self.current_level)
                elif self.game_state == 'home_screen':
                    if self.start_button.is_clicked(event, mouse_pos):
                        self.game_state = 'level_selection'
                    elif self.settings_button.is_clicked(event, mouse_pos):
                        self.game_state = 'settings'
                    elif self.quit_button.is_clicked(event, mouse_pos):
                        self.save_game_data()
                        self.running = False
                    elif self.benchmark_button.is_clicked(event, mouse_pos):
                        print("Launching Benchmark Runner...")
                        subprocess.Popen([sys.executable, "benchmark_runner.py"])
                        if pygame.mixer.get_init():
                            pygame.mixer.quit()
                elif self.game_state == 'level_selection':
                    if self.back_button.is_clicked(event, mouse_pos): 
                        self.game_state = 'home_screen'
                    if self.shop_button.is_clicked(event, mouse_pos): self.game_state = 'shop_screen'
                    if self.inventory_button.is_clicked(event, mouse_pos): self.game_state = 'inventory'

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for card in self.level_cards:
                                if card['rect'].collidepoint(mouse_pos) and card['id'] <= self.unlocked_levels:
                                    self.init_level(card['id'])
                        elif event.button == 4: self.scroll_x -= 50
                        elif event.button == 5: self.scroll_x += 50
                    
                    max_scroll_x = (len(ALL_LEVELS) - 1) * 260
                    self.scroll_x = max(0, min(self.scroll_x, max_scroll_x))
                elif self.game_state == 'inventory':
                    result = self.inventory_screen.handle_event(event)
                    if result == 'back':
                        self.game_state = 'level_selection'
                    elif isinstance(result, tuple):
                        action, p_idx, item_id = result
                        if action == 'character_selected':
                            self.change_character(p_idx, item_id)
                        elif action == 'gun_selected':
                            self.equipped_guns[p_idx] = item_id
                            for p in self.players:
                                if p.player_index == p_idx:
                                    p.equip_gun(item_id)
                            self.inventory_screen.update_data(self.selected_characters, self.unlocked_guns, self.equipped_guns, self.unlocked_characters, self.connected_players)
                elif self.game_state == 'shop_screen':
                    if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                    
                    result = self.shop_screen.handle_event(event)
                    if result == 'buy_crate':
                        self.buy_gun_crate()
                    elif result:
                        item_data = SHOP_ITEMS[result]
                        current_level = self.upgrades.get(result, 0)

                        if current_level < item_data['max_level']:
                            price = item_data['prices'][current_level]
                            if self.total_coins >= price:
                                self.total_coins -= price
                                self.upgrades[result] += 1

                                if result in CHARACTER_DATA and result not in self.unlocked_characters:
                                    self.unlocked_characters.append(result)
                                    print(f"Character '{item_data['name']}' unlocked!")
                                
                                self.save_game_data()
                                self.shop_screen.total_coins = self.total_coins
                                self.shop_screen.upgrades = self.upgrades
                                self.inventory_screen.update_data(self.selected_characters, self.unlocked_guns, self.equipped_guns, self.unlocked_characters, self.connected_players)
                elif self.game_state == 'settings':
                    if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'home_screen'

                    if self.volume_down_button.is_clicked(event, mouse_pos):
                        self.volume = max(0.0, round(self.volume - 0.1, 1))
                        self.apply_settings()
                        self.save_game_data()
                    
                    if self.volume_up_button.is_clicked(event, mouse_pos):
                        self.volume = min(1.0, round(self.volume + 0.1, 1))
                        self.apply_settings()
                        self.save_game_data()

                    if self.fullscreen_button.is_clicked(event, mouse_pos):
                        self.fullscreen = not self.fullscreen
                        self.apply_settings()
                        self.save_game_data()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error processing events: {e}")

    def init_level(self, level_number):
        self.current_level = level_number
        level_data = ALL_LEVELS[level_number]
        self.gate_type = level_data.get("gate_type", "boss")
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.boss_gate_group = pygame.sprite.Group()
        self.power_up_boxes = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        
        # Players
        self.players = []
        start_x = 100
        start_y = 400
        
        for i, player_idx in enumerate(self.connected_players):
            # Offset P2 slightly
            x_offset = i * 50 
            char_id = self.selected_characters.get(player_idx, 'cyborg')
            gun_id = self.equipped_guns.get(player_idx, 'pistol_1')
            
            p = Player(start_x + x_offset, start_y, self, upgrades=self.upgrades, character_id=char_id, equipped_gun_id=gun_id, upgrades_data=self.upgrades)
            p.player_index = player_idx # Assign index to player sprite
            self.players.append(p)
            self.all_sprites.add(p)

        self.player = self.players[0] if self.players else None # Legacy reference to P1
        
        # Level Objects
        for p_data in level_data["platforms"]:
            self.platforms.add(Platform(*p_data))
        for p_data in level_data["moving_platforms"]:
            p = MovingPlatform(*p_data)
            self.platforms.add(p)
            self.moving_platforms.add(p)
        for c_data in level_data["coins"]:
            self.coins.add(Coin(*c_data))
        for e_data in level_data["enemies"]:
            # Enemies target the closest player (simple logic for now, pass P1)
            # Improved logic: Pass list of players to Enemy or handle in Enemy.update
            # For now, Enemy takes 'player'. We'll pass P1. 
            # TODO: Update Enemy to target closest player.
            self.enemies.add(Enemy(player=self.player, **e_data))
        for b_data in level_data.get("power_up_boxes", []):
            self.power_up_boxes.add(PowerUpBox(*b_data))
        
        self.boss_gate = BossGate(level_data["boss_gate_x"], 460)
        self.boss_gate_group.add(self.boss_gate)
        
        # Add all sprites to the main rendering group
        self.all_sprites.add(
            self.platforms, 
            self.coins, 
            self.enemies, 
            self.power_up_boxes, 
            self.boss_gate
        )
        
        self.boss = None
        self.game_state = 'platformer'
        self.camera_x = 0
        
        pygame.mixer.music.stop()
        pygame.mixer.music.load(LEVEL_MUSIC)
        pygame.mixer.music.play(-1)

    def change_character(self, player_index, character_id):
        self.selected_characters[player_index] = character_id
        self.inventory_screen.update_data(self.selected_characters, self.unlocked_guns, self.equipped_guns, self.unlocked_characters)
        
        # If in level, restart level to apply changes
        if self.game_state in ['platformer', 'boss_fight']:
             self.init_level(self.current_level)
        else:
            # If in menu (not really showing players), just update data
            pass

    def update_game_state(self):
        self.benchmark.update(self.clock)
        if self.paused:
            return

        # Check for active players and Game Over condition
        if self.game_state in ['platformer', 'boss_fight']:
            alive_players = [p for p in self.players if p.health > 0]
            if not alive_players and self.players: # All dead
                pygame.mixer.music.stop()
                if self.sfx.get('walk'): self.sfx['walk'].stop()
                self.walking_sound_playing = False
                if self.death_sound: self._play_sfx('death')
                self.save_game_data()
                self.game_state = 'game_over'
                return # Stop updates

            # Update collisions for boss
            if self.boss and self.players:
                # Check collision with ANY player
                hit_players = pygame.sprite.spritecollide(self.boss, self.players, False) # Using rect for simple collision
                for p in hit_players:
                    p.take_damage(BOSS_COLLISION_DAMAGE)


        # This return statement needs to be conditional on the current game state
        # It was originally intended to stop updates in menu states, but it was too broad.
        if self.game_state not in ['platformer', 'boss_fight']: # Only update player-related stuff in gameplay states
            if self.walking_sound_playing:
                self.sfx['walk'].stop()
                self.walking_sound_playing = False
            return

        # Initialize players if needed (should be done in init_level, but safeguard)
        if not self.players and self.game_state in ['platformer', 'boss_fight']:
             self.init_level(self.current_level)

        if self.game_state == 'platformer':
            self.moving_platforms.update()
            # Enemies target the first alive player, or just the first player if all dead (to prevent crash)
            alive_players = [p for p in self.players if p.health > 0]
            primary_target = alive_players[0] if alive_players else (self.players[0] if self.players else None)
            
            self.enemies.update(primary_target, self.all_sprites, self.enemy_projectiles, self.platforms)
            
            self.enemy_projectiles.update(self.platforms)
            self.power_ups.update()
            self.boss_gate_group.update()
        elif self.game_state == 'boss_fight':
            if self.boss:
                self.boss.update()
            if self.game_state == 'victory':
                pygame.mixer.music.stop()
            self.boss_projectiles.update(self.platforms)

        actions = self.controller.get_actions()

        if actions.get('dash'): self.player.dash()
        if actions.get('shoot'):
            projectiles, sfx_name = self.player.shoot(actions.get('shoot_direction', 'horizontal'))
            if projectiles: 
                self.all_sprites.add(projectiles); self.projectiles.add(projectiles)
                if sfx_name: # No need to check sfx.get() here, helper does it
                    self._play_sfx(sfx_name)

            if actions.get('switch_weapon'):
                player.switch_weapon()

            if actions.get('activate_ultimate') and player.ultimate_ready: # Use correct key
                ultimate_proj = player.activate_ultimate()
                if ultimate_proj:
                    self.all_sprites.add(ultimate_proj)
                    self.projectiles.add(ultimate_proj)

            # Update player physics/animation
            sfx_events = player.update(actions.get('move_x'), self.platforms)
            if sfx_events:
                for sfx in sfx_events:
                    self._play_sfx(sfx)

            # Handle walking sound (simplified for multiple players: play if ANY moving)
            # This is a bit tricky with one sound channel. Maybe just play for P1 or mix?
            # Let's keep it simple: if P1 moves, play sound.
            if player.player_index == 0:
                is_moving = actions.get('move_x') is not None and (actions['move_x'] < 0.4 or actions['move_x'] > 0.6)
                if is_moving and player.on_ground and not self.walking_sound_playing:
                    self._play_sfx('walk', -1)
                    self.walking_sound_playing = True
                elif (not is_moving or not player.on_ground) and self.walking_sound_playing:
                    if self.sfx.get('walk'):
                        self.sfx['walk'].stop()
                        self.walking_sound_playing = False

            # Player Collisions (Coins, Powerups, Enemies)
            if self.game_state == 'platformer':
                # Coins
                for coin in pygame.sprite.spritecollide(player, self.coins, False):
                    if player.hitbox.colliderect(coin.rect):
                        coin.kill()
                        self.total_coins += 1
                        player.coins_collected_in_level += 1
                        self._play_sfx('coin')

                # Powerups
                hit_power_ups = pygame.sprite.spritecollide(player, self.power_ups, True)
                for power_up in hit_power_ups:
                    player.activate_power_up(power_up.power_up_type)

                # Enemies
                if pygame.sprite.spritecollide(player, self.enemies, False, collide_hitbox): 
                    player.take_damage(10)
                # Enemy Projectiles
                if pygame.sprite.spritecollide(player, self.enemy_projectiles, True): 
                    player.take_damage(15)

            # Boss Gate
            if pygame.sprite.spritecollide(player, self.boss_gate_group, False): 
                if self.gate_type == 'next_level':
                    if self.current_level == self.unlocked_levels and self.unlocked_levels < len(ALL_LEVELS):
                        self.unlocked_levels += 1
                    
                    # Bonus coins
                    for p in self.players:
                        self.total_coins += p.coins_collected_in_level
                        
                    self.save_game_data()
                    self._play_sfx('victory')
                    
                    if self.current_level < len(ALL_LEVELS):
                        self.init_level(self.current_level + 1)
                    else:
                        # Should normally be handled by boss gate type, but just in case
                        self.game_state = 'victory'
                    return
                else:
                    self.init_boss_fight()
                    return
            
            # Boss Projectiles collision
            if self.game_state == 'boss_fight':
                if pygame.sprite.spritecollide(player, self.boss_projectiles, True): 
                    player.take_damage(25)

            # Fall death
            if player.rect.top > SCREEN_HEIGHT + 200:
                player.health = 0 # Mark as dead next loop
                player.kill()

        self.projectiles.update()

        # Projectile Collisions (Enemies, Boxes)
        for proj in self.projectiles:
            hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False, lambda proj, enemy: proj.rect.colliderect(enemy.hitbox))
            if hit_enemies:
                proj.kill()
                for enemy in hit_enemies:
                    enemy.take_damage(proj.damage)
            
            hit_boxes = pygame.sprite.spritecollide(proj, self.power_up_boxes, False)
            if hit_boxes:
                proj.kill()
                for box in hit_boxes:
                    power_up_type = box.take_damage(proj.damage)
                    if power_up_type:
                        power_up = PowerUp(box.rect.centerx, box.rect.centery, power_up_type)
                        self.all_sprites.add(power_up)
                        self.power_ups.add(power_up)
            
            if pygame.sprite.spritecollide(proj, self.platforms, False):
                proj.kill()

        if self.game_state == 'boss_fight' and self.boss:
            hits = pygame.sprite.spritecollide(self.boss, self.projectiles, True)
            for hit in hits:
                self.boss.take_damage(hit.damage)
            if not self.boss.alive():
                pass # Handled by boss update

        # Update Camera
        self.update_camera()

    def update_camera(self):
        # Camera tracks average X of all alive players
        alive_players = [p for p in self.players if p.health > 0]
        if not alive_players:
            return

        avg_x = sum(p.rect.centerx for p in alive_players) / len(alive_players)
        
        level_width = self.boss_gate.rect.right + 100 
        target_camera_x = avg_x - SCREEN_WIDTH / 2
        self.camera_x = max(0, min(target_camera_x, level_width - SCREEN_WIDTH))

        if pygame.time.get_ticks() < self.screen_shake_start_time + self.screen_shake_duration:
            shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.camera_x += shake_x
        else:
            self.screen_shake_duration = 0
            self.screen_shake_intensity = 0

        self.parallax.update(self.camera_x)

    def draw_boss_health_bar(self):
        if self.boss:
            health_pct = self.boss.health / self.boss.max_health
            bar_width = SCREEN_WIDTH * 0.8
            bar_height = 25
            x = (SCREEN_WIDTH - bar_width) / 2
            y = 50
            
            # Background
            pygame.draw.rect(self.screen, GRAY, (x, y, bar_width, bar_height))
            # Health
            pygame.draw.rect(self.screen, RED, (x, y, bar_width * health_pct, bar_height))
            # Border
            pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height), 2)
            
            self.draw_text("BOSS HEALTH", 18, SCREEN_WIDTH / 2, y + bar_height / 2, WHITE)

    def draw(self):
        self.screen.fill(BLACK) # Clear screen at the beginning of each draw call
        mouse_pos = pygame.mouse.get_pos() # Define mouse_pos here

        effective_camera_x = self.camera_x
        effective_camera_y = 0 # Assuming vertical camera is fixed for now

        # Apply screen shake offsets to effective camera positions for drawing
        if pygame.time.get_ticks() < self.screen_shake_start_time + self.screen_shake_duration:
            shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            effective_camera_x += shake_x
            effective_camera_y += shake_y

        if self.game_state == 'home_screen':
            self.screen.blit(self.menu_bg_image, (0, 0))
        else:
            self.parallax.draw(self.screen)

        if self.game_state == 'home_screen':
            self.draw_text("Spoonhead", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            
            # Draw buttons
            self.start_button.draw(self.screen, mouse_pos)
            self.settings_button.draw(self.screen, mouse_pos)
            self.quit_button.draw(self.screen, mouse_pos)
            self.benchmark_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'settings' or self.game_state == 'settings_ingame':
            self.draw_text("Settings", 60, SCREEN_WIDTH/2, 100, GOLD)
            
            self.draw_text(f"Volume: {int(self.volume * 100)}%", 40, SCREEN_WIDTH/2, 225, WHITE)
            self.volume_down_button.draw(self.screen, mouse_pos)
            self.volume_up_button.draw(self.screen, mouse_pos)
            
            # Update text based on state
            self.fullscreen_button.text = "Mode: Fullscreen" if self.fullscreen else "Mode: Windowed"
            self.fullscreen_button.draw(self.screen, mouse_pos)
            self.back_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'level_selection':
            self.screen.blit(self.menu_bg_image, (0, 0))
            self.draw_text("Select Level", 40, SCREEN_WIDTH/2, 80, GOLD)
            self.draw_text(f"Total Coins: {self.total_coins}", 20, SCREEN_WIDTH/2, 140, GOLD)

            self.level_cards = []
            card_width, card_height = 220, 300
            padding = 40
            start_x = SCREEN_WIDTH / 2 - card_width / 2
            
            for i, (level_num, level_data) in enumerate(ALL_LEVELS.items()):
                card_x = start_x + (i * (card_width + padding)) - self.scroll_x
                card_rect = pygame.Rect(card_x, SCREEN_HEIGHT / 2 - card_height / 2, card_width, card_height)
                self.level_cards.append({'id': level_num, 'rect': card_rect})

                is_unlocked = level_num <= self.unlocked_levels
                
                # Hover effect
                is_hovered = card_rect.collidepoint(mouse_pos) and is_unlocked
                
                card_color = DARK_GRAY if is_unlocked else BLACK
                border_color = YELLOW if is_hovered else (GOLD if is_unlocked else GRAY)

                pygame.draw.rect(self.screen, card_color, card_rect, border_radius=15)
                pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=15)

                # Placeholder for thumbnail
                thumb_rect = pygame.Rect(card_x + 20, card_rect.y + 20, card_width - 40, 120)
                pygame.draw.rect(self.screen, (50, 50, 50), thumb_rect)
                self.draw_text(str(level_num), 50, thumb_rect.centerx, thumb_rect.centery, border_color)

                level_name_parts = level_data['name'].split(' ', 1)
                if len(level_name_parts) > 1:
                    self.draw_text(level_name_parts[0], 20, card_rect.centerx, card_rect.y + 165, WHITE)
                    self.draw_text(level_name_parts[1], 20, card_rect.centerx, card_rect.y + 195, WHITE)
                else:
                    self.draw_text(level_data['name'], 20, card_rect.centerx, card_rect.y + 180, WHITE)

                if not is_unlocked:
                    lock_overlay = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                    lock_overlay.fill((0, 0, 0, 180))
                    self.screen.blit(lock_overlay, card_rect.topleft)
                    self.draw_text("Locked", 30, card_rect.centerx, card_rect.centery, RED)
            
            # P2 Join Text
            if 1 not in self.connected_players:
                if self.controller_manager.has_p2_device():
                    self.draw_text("P2: Press START/JUMP to Join", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, GREEN)
                else:
                    self.draw_text("Connect Controller for P2", 16, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, GRAY)
            else:
                 self.draw_text("P2 Joined!", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, BLUE)

            self.back_button.draw(self.screen, mouse_pos)
            self.shop_button.draw(self.screen, mouse_pos)
            self.inventory_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'shop_screen':
            self.shop_screen.draw()
            self.back_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'inventory':
            self.inventory_screen.draw()
        
        elif self.game_state in ['platformer', 'boss_fight', 'victory', 'game_over']:
            for sprite in self.all_sprites: 
                offset_x = sprite.rect.x - effective_camera_x
                offset_y = sprite.rect.y - effective_camera_y
                
                if isinstance(sprite, Boss) and sprite.dying_state == 'exploding':
                    explosion_center_x = sprite.rect.centerx - effective_camera_x
                    explosion_center_y = sprite.rect.centery - effective_camera_y
                    explosion_rect = sprite.image.get_rect(center=(explosion_center_x, explosion_center_y))
                    self.screen.blit(sprite.image, explosion_rect)
                else:
                    self.screen.blit(sprite.image, (offset_x, offset_y))
                
                # Draw P1/P2 indicators above players
                if isinstance(sprite, Player) and sprite.health > 0:
                    indicator_text = f"P{sprite.player_index + 1}"
                    indicator_color = GREEN if sprite.player_index == 0 else BLUE
                    self.draw_text(indicator_text, 12, offset_x + sprite.rect.width/2, offset_y - 20, indicator_color)

            if self.game_state in ['platformer', 'boss_fight']:
                for player in self.players:
                    if player.health > 0:
                        self.draw_ui(player)
            
            self.level_select_button.draw(self.screen, mouse_pos)

            if self.game_state == 'boss_fight':
                self.draw_boss_health_bar()

            if self.game_state in ['victory', 'game_over']:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 128)); self.screen.blit(overlay, (0, 0))
                if self.game_state == 'victory':
                    self.draw_text("VICTORY!", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, GOLD)
                    if self.current_level == self.unlocked_levels and self.unlocked_levels < len(ALL_LEVELS): self.draw_text(f"Level {self.current_level + 1} Unlocked!", 30, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60)
                    self.draw_text("Press any key to continue", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100)
                else:
                    self.draw_text("GAME OVER", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, RED); self.draw_text("Press R to Restart Level", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)
        
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("Paused", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            self.resume_button.draw(self.screen, pygame.mouse.get_pos())
            self.settings_button_ingame.draw(self.screen, pygame.mouse.get_pos())
            self.main_menu_button.draw(self.screen, pygame.mouse.get_pos())

        self.benchmark.draw(self.screen)
        pygame.display.flip()

    def draw_ui(self, player):
        idx = player.player_index
        
        # UI Positioning
        if idx == 0: # Left Side
            x_offset = 20
            color = GREEN
        else: # Right Side
            x_offset = SCREEN_WIDTH - 220
            color = BLUE
            
        y_offset = 20
        
        # Health bar
        health_rect = pygame.Rect(x_offset, y_offset, 200, 25)
        pygame.draw.rect(self.screen, RED, health_rect)
        
        current_health_width = (player.health / player.max_health) * 200
        current_health_rect = pygame.Rect(x_offset, y_offset, current_health_width, 25)
        pygame.draw.rect(self.screen, color, current_health_rect)
        
        # Info text
        info_x = x_offset + 100
        self.draw_text(f"P{idx+1} Health: {player.health}", 14, info_x, y_offset + 12, BLACK)
        
        # Shared Coins (Only draw once or for both?) Draw for P1 for now or top center
        if idx == 0:
            self.draw_text(f"Coins: {self.total_coins}", 20, 10, 90, GOLD, align="topleft")
        
        # Weapon
        current_weapon_name = player.unlocked_weapons[player.current_weapon_index].replace('_', ' ').title()
        self.draw_text(f"Wpn: {current_weapon_name}", 16, x_offset, y_offset + 35, WHITE, align="topleft")

        # Ultimate
        if player.ultimate_ready:
            ult_color = YELLOW if pygame.time.get_ticks() % 500 < 250 else RED
            self.draw_text("ULT READY!", 16, x_offset, y_offset + 55, ult_color, align="topleft")
        else:
            self.draw_text(f"Ult: {player.ultimate_meter}/{player.ultimate_max_meter}", 16, x_offset, y_offset + 55, WHITE, align="topleft")

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(0)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()