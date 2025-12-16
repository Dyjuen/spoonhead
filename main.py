import pygame
import os
import json
import random
from settings import *
from controller import XboxController
from sprites import Player, Boss, Projectile, BossProjectile, Platform, MovingPlatform, Coin, Enemy, BossGate, PowerUpBox, PowerUp, EnemyProjectile
from ui import Button
from level_data import ALL_LEVELS
from shop_data import SHOP_ITEMS
from shop import ShopScreen
from gun_data import GUN_DATA
from inventory import InventoryScreen, TIER_COLORS # Import TIER_COLORS

SAVE_FILE = 'save.json'

class Game:
    """Main game class with a multi-level structure and persistence."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        self.gacha_result = None
        self.gacha_animation_timer = 0
        self.gacha_gun_display_images = {} # For displaying gun in gacha animation

        self.unlocked_levels = 1
        self.total_coins = 0
        self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
        self.current_level = 1 # Change from 0 to 1
        self.unlocked_characters = ['cyborg'] # Default unlocked character
        self.selected_character = 'cyborg' # Default selected character
        self.unlocked_guns = ['pistol_1'] # Default unlocked gun
        self.equipped_gun_id = 'pistol_1' # Default equipped gun
        self.load_game_data()

        self.controller = XboxController()
        self.camera_x = 0
        self.player = None
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
        self.inventory_screen = InventoryScreen(self.screen, self.selected_character, self.unlocked_guns, GUN_DATA, CHARACTER_DATA, self.equipped_gun_id)

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
                self.selected_character = data.get('selected_character', 'cyborg')
                self.unlocked_guns = data.get('unlocked_guns', ['pistol_1'])
                self.equipped_gun_id = data.get('equipped_gun_id', 'pistol_1')

        except (FileNotFoundError, json.JSONDecodeError):
            print("Save file not found, starting new game.")
            self.unlocked_levels = 1
            self.total_coins = 0
            self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
            self.current_level = 1
            self.unlocked_characters = ['cyborg']
            self.selected_character = 'cyborg'
            self.unlocked_guns = ['pistol_1']
            self.equipped_gun_id = 'pistol_1'
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
            'selected_character': self.selected_character,
            'unlocked_guns': self.unlocked_guns,
            'equipped_gun_id': self.equipped_gun_id
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
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def load_assets(self):
        try:
            self.bg_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.jpg")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.boss_bg_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg2.jpg")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
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
            }
            self.death_sound = self.sfx['death'] # Keep separate reference for existing logic
        except pygame.error as e:
            print(f"Warning: Could not load assets: {e}")
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.bg_image.fill(SKY_BLUE)
            self.boss_bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.boss_bg_image.fill(DARK_GRAY)
            self.sfx = {}
            self.death_sound = None
        self.start_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Start Game", BLUE, PURPLE)
        self.quit_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Quit Game", RED, PURPLE)
        self.settings_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 90, 200, 50, "Settings", GRAY, PURPLE)
        
        self.level_cards = []

        self.shop_button = Button(SCREEN_WIDTH - 170, 20, 150, 50, "Shop", GOLD, PURPLE)
        self.inventory_button = Button(SCREEN_WIDTH - 170, 90, 150, 50, "Inventory", GOLD, PURPLE)
        self.back_button = Button(20, 20, 150, 50, "Back", RED, PURPLE)

        # Settings screen buttons
        self.volume_down_button = Button(SCREEN_WIDTH/2 - 150, 275, 50, 50, "-", RED, PURPLE)
        self.volume_up_button = Button(SCREEN_WIDTH/2 + 100, 275, 50, 50, "+", GREEN, PURPLE)
        self.fullscreen_button = Button(SCREEN_WIDTH/2 - 150, 350, 300, 50, "Toggle Fullscreen", BLUE, PURPLE)

        # Pause menu buttons
        self.resume_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Resume", BLUE, PURPLE)
        self.main_menu_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Main Menu", RED, PURPLE)
        
        # Load gacha gun display images
        for gun_id, gun_info in GUN_DATA.items():
            try:
                img = pygame.image.load(gun_info['image_path']).convert_alpha()
                self.gacha_gun_display_images[gun_id] = pygame.transform.scale(img, (100, 100)) # Larger scale for display
            except pygame.error:
                print(f"Warning: Could not load gacha display image for {gun_id}: {gun_info['image_path']}")
                self.gacha_gun_display_images[gun_id] = pygame.Surface((100, 100), pygame.SRCALPHA)
                self.gacha_gun_display_images[gun_id].fill(GRAY)


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
        self.player = Player(100, 400, self, upgrades=self.upgrades, character_id=self.selected_character, equipped_gun_id=self.equipped_gun_id)
        
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
            b = PowerUpBox(*b_data)
            self.power_up_boxes.add(b)
            self.platforms.add(b)
        
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

    def buy_gun_crate(self):
        crate_cost = 500
        if self.total_coins >= crate_cost:
            self.total_coins -= crate_cost

            rarity_weights = { 'Common': 0.6, 'Rare': 0.25, 'Epic': 0.1, 'Legendary': 0.05 }
            guns_by_tier = {tier: [] for tier in rarity_weights}
            for gun_id, gun_data in GUN_DATA.items():
                guns_by_tier[gun_data['tier']].append(gun_id)

            chosen_tier = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()), k=1)[0]
            
            if guns_by_tier[chosen_tier]:
                unlocked_gun_id = random.choice(guns_by_tier[chosen_tier])
                
                is_duplicate = unlocked_gun_id in self.unlocked_guns
                if is_duplicate:
                    refund = crate_cost // 2
                    self.total_coins += refund
                else:
                    self.unlocked_guns.append(unlocked_gun_id)

                self.gacha_result = {
                    'gun_id': unlocked_gun_id,
                    'is_duplicate': is_duplicate,
                    'tier': chosen_tier
                }
                self.game_state = 'gacha_animation'
                self.gacha_animation_timer = pygame.time.get_ticks()
                self.inventory_screen.update_data(self.selected_character, self.unlocked_guns, self.equipped_gun_id)
                self.save_game_data()
            else:
                print("No guns in the chosen tier.")
        else:
            print("Not enough coins to buy a crate.")

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self.save_game_data()
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.game_state in ['platformer', 'boss_fight']:
                    self.paused = not self.paused
                if event.key == pygame.K_u and self.game_state in ['platformer', 'boss_fight'] and not self.paused:
                    self.u_pressed = True

            if self.paused:
                if self.resume_button.is_clicked(event, mouse_pos):
                    self.paused = False
                elif self.main_menu_button.is_clicked(event, mouse_pos):
                    self.paused = False
                    self.total_coins += self.player.coins
                    self.save_game_data()
                    self.game_state = 'home_screen'
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(THEME_MUSIC)
                    pygame.mixer.music.play(-1)
                return # Don't process other events when paused


            
            if self.game_state == 'victory':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: 
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
            elif self.game_state == 'level_selection':
                if self.back_button.is_clicked(event, mouse_pos): 
                    self.game_state = 'home_screen'
                if self.shop_button.is_clicked(event, mouse_pos): self.game_state = 'shop_screen'
                if self.inventory_button.is_clicked(event, mouse_pos): self.game_state = 'inventory'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        for card in self.level_cards:
                            if card['rect'].collidepoint(mouse_pos) and card['id'] <= self.unlocked_levels:
                                self.init_level(card['id'])
                    elif event.button == 4: # Scroll up
                        self.scroll_x -= 50
                    elif event.button == 5: # Scroll down
                        self.scroll_x += 50
                
                # Clamp scroll
                max_scroll_x = (len(ALL_LEVELS) - 1) * 260 # Rough estimate
                self.scroll_x = max(0, min(self.scroll_x, max_scroll_x))
            elif self.game_state == 'inventory':
                result = self.inventory_screen.handle_event(event)
                if result == 'back':
                    self.game_state = 'level_selection'
                elif isinstance(result, tuple):
                    if result[0] == 'character_selected':
                        self.change_character(result[1])
                    elif result[0] == 'gun_selected':
                        self.equipped_gun_id = result[1]
                        if self.player:
                            self.player.equip_gun(self.equipped_gun_id)
                        self.inventory_screen.update_data(self.selected_character, self.unlocked_guns, self.equipped_gun_id)
            elif self.game_state == 'shop_screen':
                if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                
                result = self.shop_screen.handle_event(event)
                if result == 'buy_crate':
                    self.buy_gun_crate()
                elif result: # Should be an item_id for an upgrade
                    item_data = SHOP_ITEMS[result]
                    current_level = self.upgrades.get(result, 0)

                    if current_level < item_data['max_level']:
                        price = item_data['prices'][current_level]
                        if self.total_coins >= price:
                            self.total_coins -= price
                            self.upgrades[result] += 1
                            self.save_game_data()
                            self.shop_screen.total_coins = self.total_coins
                            self.shop_screen.upgrades = self.upgrades
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

    def change_character(self, character_id):
        self.selected_character = character_id
        self.inventory_screen.update_data(self.selected_character, self.unlocked_guns, self.equipped_gun_id)
        # We need to re-initialize the player and inventory screen to reflect the change
        # A full re-initialization of the level is the simplest way to do this for now
        if self.game_state == 'platformer' or self.game_state == 'boss_fight':
             self.init_level(self.current_level)
        else:
            # If we are not in a level, we can just recreate the player object
            self.player = Player(0, 0, self, upgrades=self.upgrades, character_id=self.selected_character)
            self.inventory_screen.update_data(self.selected_character, self.unlocked_guns, self.equipped_gun_id)

    def update_game_state(self):
        if self.paused:
            return

        # Player death check moved inside gameplay state condition
        if self.game_state in ['platformer', 'boss_fight']:
            if self.player and self.player.health <= 0:
                pygame.mixer.music.stop()
                if self.sfx.get('walk'): self.sfx['walk'].stop()
                self.walking_sound_playing = False
                if self.death_sound: self.death_sound.play()
                self.total_coins += self.player.coins
                self.save_game_data()
                self.game_state = 'game_over'

            # Check for player-boss collision damage
            if self.boss and self.player:
                if pygame.sprite.spritecollide(self.player, self.boss_group, False):
                    self.player.take_damage(BOSS_COLLISION_DAMAGE)


        # This return statement needs to be conditional on the current game state
        # It was originally intended to stop updates in menu states, but it was too broad.
        if self.game_state not in ['platformer', 'boss_fight', 'gacha_animation']: # Only update player-related stuff in gameplay states
            if self.walking_sound_playing:
                self.sfx['walk'].stop()
                self.walking_sound_playing = False
            return

        # Only proceed with player updates if in a gameplay state AND player exists
        if not self.player and self.game_state in ['platformer', 'boss_fight']:
            # This case should ideally not happen if init_level is called correctly
            print("Warning: Player is None in gameplay state, attempting to re-initialize.")
            self.player = Player(0, 0, self, upgrades=self.upgrades, character_id=self.selected_character, equipped_gun_id=self.equipped_gun_id)
            self.all_sprites.add(self.player)


        if self.game_state == 'platformer':
            self.moving_platforms.update()
            self.enemies.update(self.player, self.all_sprites, self.enemy_projectiles)
            self.enemy_projectiles.update(self.platforms)
            self.power_ups.update()
        elif self.game_state == 'boss_fight':
            # Update boss and boss projectiles
            if self.boss:
                self.boss.update()
            self.boss_projectiles.update(self.platforms)
        elif self.game_state == 'gacha_animation': # Gacha animation handles its own state transition
            if pygame.time.get_ticks() - self.gacha_animation_timer > 3000: # 3 seconds
                self.game_state = 'shop_screen'
                self.gacha_result = None
            return # Don't run player update logic during gacha animation

        actions = self.controller.get_actions()
        if actions.get('jump'): 
            sfx_to_play = self.player.jump()
            if sfx_to_play and self.sfx.get(sfx_to_play):
                self.sfx[sfx_to_play].play()

        if actions.get('dash'): self.player.dash()
        if actions.get('shoot'):
            projectiles, sfx_name = self.player.shoot(actions.get('shoot_direction', 'horizontal'))
            if projectiles: 
                self.all_sprites.add(projectiles); self.projectiles.add(projectiles)
                if sfx_name and self.sfx.get(sfx_name):
                    self.sfx[sfx_name].play()

        if actions.get('switch_weapon'):
            self.player.switch_weapon()

        if self.u_pressed and self.player.ultimate_ready:
            ultimate_proj = self.player.activate_ultimate()
            if ultimate_proj:
                self.all_sprites.add(ultimate_proj)
                self.projectiles.add(ultimate_proj)
            self.u_pressed = False # Reset the flag after processing

        sfx_events = self.player.update(actions.get('move_x'), self.platforms)
        if sfx_events:
            for sfx in sfx_events:
                if self.sfx.get(sfx):
                    self.sfx[sfx].play()

        self.projectiles.update()

        # Handle walking sound
        if self.game_state in ['platformer', 'boss_fight']:
            is_moving = actions.get('move_x') is not None and (actions['move_x'] < 0.4 or actions['move_x'] > 0.6)
            if is_moving and self.player.on_ground and not self.walking_sound_playing:
                if self.sfx.get('walk'):
                    self.sfx['walk'].play(-1)  # Loop
                    self.walking_sound_playing = True
            elif (not is_moving or not self.player.on_ground) and self.walking_sound_playing:
                if self.sfx.get('walk'):
                    self.sfx['walk'].stop()
                    self.walking_sound_playing = False

        if self.game_state == 'platformer':
            self.coins.update()

            if pygame.sprite.spritecollide(self.player, self.coins, True): 
                self.player.coins += 1
                if self.sfx.get('coin'):
                    self.sfx['coin'].play()

            hit_power_ups = pygame.sprite.spritecollide(self.player, self.power_ups, True)
            for power_up in hit_power_ups:
                self.player.activate_power_up(power_up.power_up_type)

            if pygame.sprite.spritecollide(self.player, self.enemies, False): 
                self.player.take_damage(10)
            if pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True): 
                self.player.take_damage(15)

            for proj in self.projectiles:
                hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False)
                if hit_enemies:
                    proj.kill()
                    for enemy in hit_enemies:
                        enemy.take_damage(proj.damage)
                
                hit_boxes = pygame.sprite.spritecollide(proj, self.power_up_boxes, False)
                if hit_boxes:
                    proj.kill()
                    for box in hit_boxes:
                        if box.take_damage(proj.damage): # If box is destroyed
                            # Spawn a PowerUp at the box's position
                            power_up = PowerUp(box.rect.centerx, box.rect.centery, box.power_up_type)
                            self.all_sprites.add(power_up)
                            self.power_ups.add(power_up)
                
                # Check for collision with platforms
                if pygame.sprite.spritecollide(proj, self.platforms, False):
                    proj.kill()

            if pygame.sprite.spritecollide(self.player, self.boss_gate_group, False): 
                self.init_boss_fight()
            self.update_camera()

        elif self.game_state == 'boss_fight':
            # Boss takes damage from player projectiles
            if self.boss:
                hits = pygame.sprite.spritecollide(self.boss, self.projectiles, True)
                for hit in hits:
                    self.boss.take_damage(hit.damage)
            
            # Player takes damage from boss projectiles
            if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True): 
                self.player.take_damage(25)

        if self.player.rect.top > SCREEN_HEIGHT + 200: 
            self.total_coins += self.player.coins
            self.save_game_data()
            self.game_state = 'game_over'

        if self.boss and not self.boss.alive() and self.game_state == 'boss_fight':
            self.game_state = 'victory'; self.total_coins += self.player.coins
            pygame.mixer.music.stop()
            if self.sfx.get('victory'):
                self.sfx['victory'].play()
            if self.sfx.get('walk'): self.sfx['walk'].stop()
            self.walking_sound_playing = False
            if self.current_level == self.unlocked_levels and self.unlocked_levels < len(ALL_LEVELS): self.unlocked_levels += 1
            self.save_game_data()

    def update_camera(self):
        # Simple camera that keeps the player in the middle of the screen
        # The camera should not go beyond the level boundaries
        level_width = self.boss_gate.rect.right + 100 # Approximate level width
        
        # Target camera position
        target_camera_x = self.player.rect.centerx - SCREEN_WIDTH / 2
        
        # Clamp camera position to level boundaries
        self.camera_x = max(0, min(target_camera_x, level_width - SCREEN_WIDTH))

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
        mouse_pos = pygame.mouse.get_pos()
        current_bg = self.boss_bg_image if self.game_state in ['boss_fight', 'victory'] else self.bg_image
        self.screen.blit(current_bg, (0, 0))

        if self.game_state == 'home_screen':
            self.draw_text("Spoonhead", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            
            # Draw buttons
            self.start_button.draw(self.screen, mouse_pos)
            self.settings_button.draw(self.screen, mouse_pos)
            self.quit_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'settings':
            self.draw_text("Settings", 60, SCREEN_WIDTH/2, 100, GOLD)
            
            self.draw_text(f"Volume: {int(self.volume * 100)}%", 40, SCREEN_WIDTH/2, 225, WHITE)
            self.volume_down_button.draw(self.screen, mouse_pos)
            self.volume_up_button.draw(self.screen, mouse_pos)
            
            # Update text based on state
            self.fullscreen_button.text = "Mode: Fullscreen" if self.fullscreen else "Mode: Windowed"
            self.fullscreen_button.draw(self.screen, mouse_pos)
            self.back_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'level_selection':
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

                self.draw_text(level_data['name'], 18, card_rect.centerx, card_rect.y + 180, WHITE)

                if not is_unlocked:
                    lock_overlay = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                    lock_overlay.fill((0, 0, 0, 180))
                    self.screen.blit(lock_overlay, card_rect.topleft)
                    self.draw_text("Locked", 30, card_rect.centerx, card_rect.centery, RED)

            self.back_button.draw(self.screen, mouse_pos)
            self.shop_button.draw(self.screen, mouse_pos)
            self.inventory_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'shop_screen':
            self.shop_screen.draw()
            self.back_button.draw(self.screen, mouse_pos)
        elif self.game_state == 'inventory':
            self.inventory_screen.draw()
        elif self.game_state == 'gacha_animation':
            self.screen.fill(BLACK)
            if self.gacha_result:
                gun_id = self.gacha_result['gun_id']
                gun_data = GUN_DATA[gun_id]
                
                # Tier color
                tier_color = WHITE
                if self.gacha_result['tier'] == 'Rare':
                    tier_color = BLUE
                elif self.gacha_result['tier'] == 'Epic':
                    tier_color = PURPLE
                elif self.gacha_result['tier'] == 'Legendary':
                    tier_color = GOLD

                # Gun Image with scaling animation
                animation_time = pygame.time.get_ticks() - self.gacha_animation_timer
                scale_factor = min(1.0, animation_time / 1500) # Grow over 1.5 seconds
                current_gun_image = self.gacha_gun_display_images[gun_id]
                
                scaled_width = int(current_gun_image.get_width() * scale_factor)
                scaled_height = int(current_gun_image.get_height() * scale_factor)
                
                if scaled_width > 0 and scaled_height > 0:
                    display_gun_image = pygame.transform.scale(current_gun_image, (scaled_width, scaled_height))
                    gun_rect = display_gun_image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150))
                    self.screen.blit(display_gun_image, gun_rect)

                    # Draw tier border around the gun
                    border_size = 5
                    pygame.draw.rect(self.screen, tier_color, gun_rect.inflate(border_size * 2, border_size * 2), border_size, border_radius=10)


                self.draw_text(gun_data['name'], 50, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, tier_color)
                self.draw_text(f"({self.gacha_result['tier']})", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, tier_color)

                if self.gacha_result['is_duplicate']:
                    self.draw_text("Duplicate!", 40, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 180, RED)
                    self.draw_text(f"Refunded {500 // 2} coins", 20, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 220, YELLOW)
                else:
                    self.draw_text("New Gun Unlocked!", 40, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 180, GREEN)
        elif self.game_state in ['platformer', 'boss_fight', 'victory', 'game_over']:
            if self.game_state == 'platformer':
                for sprite in self.all_sprites: self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
                
                # DEBUG: Draw hitboxes
                for enemy in self.enemies:
                    pygame.draw.rect(self.screen, (255, 0, 0), enemy.rect.move(-self.camera_x, 0), 1)
                for proj in self.projectiles:
                    pygame.draw.rect(self.screen, (0, 255, 255), proj.rect.move(-self.camera_x, 0), 1)
                
                # DEBUG: Draw player collision box
                if self.player and self.player.alive():
                    pygame.draw.rect(self.screen, (0, 255, 0), self.player.hitbox.move(-self.camera_x, 0), 2)

            else: 
                self.all_sprites.draw(self.screen)
            
            if self.player and self.player.alive(): self.draw_ui()

            if self.game_state == 'boss_fight':
                self.draw_boss_health_bar()

            if self.game_state in ['victory', 'game_over']:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 128)); self.screen.blit(overlay, (0, 0))
                if self.game_state == 'victory':
                    self.draw_text("VICTORY!", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, GOLD)
                    if self.current_level == self.unlocked_levels and self.unlocked_levels < len(ALL_LEVELS): self.draw_text(f"Level {self.unlocked_levels} Unlocked!", 30, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60)
                    self.draw_text("Press any key to continue", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100)
                else:
                    self.draw_text("GAME OVER", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, RED); self.draw_text("Press R to Restart Level", 20, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)
        
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("Paused", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            self.resume_button.draw(self.screen, pygame.mouse.get_pos())
            self.main_menu_button.draw(self.screen, pygame.mouse.get_pos())

        pygame.display.flip()

    def draw_ui(self, player_alive=True): # Added player_alive argument
        # Health bar
        health_rect = pygame.Rect(20, 20, 200, 25)
        pygame.draw.rect(self.screen, RED, health_rect)
        
        current_health_width = (self.player.health / self.player.max_health) * 200
        current_health_rect = pygame.Rect(20, 20, current_health_width, 25)
        pygame.draw.rect(self.screen, GREEN, current_health_rect)
        
        self.draw_text(f"Health: {self.player.health}", 18, 120, 32)
        
        # Coins
        self.draw_text(f"Coins: {self.total_coins}", 20, SCREEN_WIDTH - 100, 30, GOLD) # Changed to self.total_coins
        
        # Current Weapon
        current_weapon_name = self.player.unlocked_weapons[self.player.current_weapon_index].replace('_', ' ').title()
        self.draw_text(f"Weapon: {current_weapon_name}", 20, SCREEN_WIDTH - 100, 60, WHITE)

        # Ultimate Meter
        if self.player.ultimate_ready:
            self.draw_text("ULTIMATE READY!", 20, SCREEN_WIDTH / 2, 90, YELLOW)
        else:
            self.draw_text(f"Ultimate: {self.player.ultimate_meter}/{self.player.ultimate_max_meter}", 20, SCREEN_WIDTH / 2, 90, WHITE)

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()