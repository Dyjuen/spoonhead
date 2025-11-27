import pygame
import os
import json
from settings import *
from controller import XboxController
from sprites import Player, Boss, Projectile, BossProjectile, Platform, MovingPlatform, Coin, Enemy, BossGate, PowerUpBox, PowerUp, EnemyProjectile
from ui import Button
from level_data import ALL_LEVELS
from shop_data import SHOP_ITEMS
from shop import ShopScreen

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
        self.running = True
        self.game_state = 'home_screen'

        # Game settings
        self.volume = 1.0
        self.fullscreen = False
        self.paused = False
        self.walking_sound_playing = False
        self.q_pressed = False

        self.unlocked_levels = 1
        self.total_coins = 0
        self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
        self.current_level = 0
        self.load_game_data()

        self.controller = XboxController()
        self.camera_x = 0
        self.player = None
        
        self.load_assets()
        self.setup_buttons()
        self.shop_screen = ShopScreen(self.screen, self.total_coins, self.upgrades, SHOP_ITEMS)

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
        except (FileNotFoundError, json.JSONDecodeError):
            print("Save file not found, starting new game.")
            self.upgrades = {item_id: 0 for item_id in SHOP_ITEMS}
            self.volume = 1.0
            self.fullscreen = False

    def save_game_data(self):
        data = {
            'unlocked_levels': self.unlocked_levels, 
            'total_coins': self.total_coins, 
            'upgrades': self.upgrades,
            'volume': self.volume,
            'fullscreen': self.fullscreen
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

    def setup_buttons(self):
        self.start_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Start Game", BLUE, PURPLE)
        self.quit_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Quit Game", RED, PURPLE)
        self.settings_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 90, 200, 50, "Settings", GRAY, PURPLE)
        
        self.level_buttons = []
        for i in range(1, len(ALL_LEVELS) + 1):
            y_pos = SCREEN_HEIGHT/2 - 100 + (i-1)*80
            self.level_buttons.append(Button(SCREEN_WIDTH/2 - 150, y_pos, 300, 60, f"Level {i}", GREEN, PURPLE))

        self.shop_button = Button(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 70, 150, 50, "Shop", GOLD, PURPLE)
        self.back_button = Button(20, SCREEN_HEIGHT - 70, 150, 50, "Back", RED, PURPLE)

        # Settings screen buttons
        self.volume_down_button = Button(SCREEN_WIDTH/2 - 150, 200, 50, 50, "-", RED, PURPLE)
        self.volume_up_button = Button(SCREEN_WIDTH/2 + 100, 200, 50, 50, "+", GREEN, PURPLE)
        self.fullscreen_button = Button(SCREEN_WIDTH/2 - 150, 300, 300, 50, "Toggle Fullscreen", BLUE, PURPLE)

        # Pause menu buttons
        self.resume_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Resume", BLUE, PURPLE)
        self.main_menu_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Main Menu", RED, PURPLE)

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
        self.player = Player(100, 400, self.upgrades)
        
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
            self.power_up_boxes.add(PowerUpBox(*b_data, game=self))
        
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
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self.save_game_data()
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.game_state in ['platformer', 'boss_fight']:
                    self.paused = not self.paused
                if event.key == pygame.K_q and self.game_state in ['platformer', 'boss_fight'] and not self.paused:
                    self.q_pressed = True

            if self.paused:
                if self.resume_button.is_clicked(event, mouse_pos):
                    self.paused = False
                elif self.main_menu_button.is_clicked(event, mouse_pos):
                    self.paused = False
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
                if self.start_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                elif self.quit_button.is_clicked(event, mouse_pos): 
                    self.save_game_data()
                    self.running = False
                elif self.settings_button.is_clicked(event, mouse_pos): self.game_state = 'settings'
            elif self.game_state == 'level_selection':
                if self.back_button.is_clicked(event, mouse_pos): 
                    self.game_state = 'home_screen'
                if self.shop_button.is_clicked(event, mouse_pos): self.game_state = 'shop_screen'
                for i, button in enumerate(self.level_buttons):
                    if i < self.unlocked_levels and button.is_clicked(event, mouse_pos): self.init_level(i + 1)
            elif self.game_state == 'shop_screen':
                if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                
                purchased_item_id = self.shop_screen.handle_event(event)
                if purchased_item_id:
                    item_data = SHOP_ITEMS[purchased_item_id]
                    current_level = self.upgrades.get(purchased_item_id, 0)

                    if current_level < item_data['max_level']:
                        price = item_data['prices'][current_level]
                        if self.total_coins >= price:
                            self.total_coins -= price
                            self.upgrades[purchased_item_id] += 1
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

    def update_game_state(self):
        if self.paused:
            return

        is_gameplay_state = self.game_state in ['platformer', 'boss_fight']
        
        if self.player and self.player.health <= 0 and is_gameplay_state:
            pygame.mixer.music.stop()
            if self.sfx.get('walk'): self.sfx['walk'].stop()
            self.walking_sound_playing = False
            if self.death_sound: self.death_sound.play()
            self.game_state = 'game_over'

        if self.game_state in ['victory', 'game_over', 'home_screen', 'level_selection', 'shop_screen', 'settings']: 
            if self.walking_sound_playing:
                self.sfx['walk'].stop()
                self.walking_sound_playing = False
            return

        if self.game_state == 'platformer':
            self.moving_platforms.update()
            self.enemies.update(self.player, self.all_sprites, self.enemy_projectiles)
            self.enemy_projectiles.update()
            self.power_ups.update()
        elif self.game_state == 'boss_fight':
            # Update boss and boss projectiles
            if self.boss:
                self.boss.update()
            self.boss_projectiles.update()

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

        if self.q_pressed and self.player.ultimate_ready:
            ultimate_proj = self.player.activate_ultimate()
            if ultimate_proj:
                self.all_sprites.add(ultimate_proj)
                self.projectiles.add(ultimate_proj)
            self.q_pressed = False # Reset the flag after processing

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
                        box.take_damage(proj.damage)

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
            
            self.draw_text("BOSS HEALTH", 24, SCREEN_WIDTH / 2, y + bar_height / 2, WHITE)

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        current_bg = self.boss_bg_image if self.game_state in ['boss_fight', 'victory'] else self.bg_image
        self.screen.blit(current_bg, (0, 0))

        if self.game_state == 'home_screen':
            self.draw_text("Spoonhead", 100, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            self.start_button.draw(self.screen, pygame.mouse.get_pos())
            self.quit_button.draw(self.screen, pygame.mouse.get_pos())
            self.settings_button.draw(self.screen, pygame.mouse.get_pos())
        elif self.game_state == 'level_selection':
            self.draw_text("Select Level", 80, SCREEN_WIDTH/2, 60, GOLD); self.draw_text(f"Total Coins: {self.total_coins}", 40, SCREEN_WIDTH/2, 120, GOLD)
            for i, button in enumerate(self.level_buttons):
                button.text = f"Level {i+1}: {ALL_LEVELS[i+1]['name']}" if i < self.unlocked_levels else f"Level {i+1} (Locked)"
                button.color = GREEN if i < self.unlocked_levels else GRAY
                button.draw(self.screen, pygame.mouse.get_pos())
            self.back_button.draw(self.screen, pygame.mouse.get_pos()); self.shop_button.draw(self.screen, pygame.mouse.get_pos())
        elif self.game_state == 'shop_screen':
            self.shop_screen.draw()
            self.back_button.draw(self.screen, pygame.mouse.get_pos())
        elif self.game_state == 'settings':
            self.draw_text("Settings", 80, SCREEN_WIDTH/2, 60, GOLD)
            
            # Volume control
            self.draw_text("Volume", 40, SCREEN_WIDTH/2, 150, WHITE)
            self.volume_down_button.draw(self.screen, mouse_pos)
            self.draw_text(f"{int(self.volume * 100)}%", 50, SCREEN_WIDTH/2, 225, WHITE)
            self.volume_up_button.draw(self.screen, mouse_pos)

            # Fullscreen toggle
            self.fullscreen_button.text = f"Mode: {'Fullscreen' if self.fullscreen else 'Windowed'}"
            self.fullscreen_button.draw(self.screen, mouse_pos)

            self.back_button.draw(self.screen, pygame.mouse.get_pos())
        elif self.game_state in ['platformer', 'boss_fight', 'victory', 'game_over']:
            if self.game_state == 'platformer':
                for sprite in self.all_sprites: self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
                
                # DEBUG: Draw hitboxes
                for enemy in self.enemies:
                    pygame.draw.rect(self.screen, (255, 0, 0), enemy.rect.move(-self.camera_x, 0), 1)
                for proj in self.projectiles:
                    pygame.draw.rect(self.screen, (0, 255, 255), proj.rect.move(-self.camera_x, 0), 1)

            else: 
                self.all_sprites.draw(self.screen)
            
            if self.player and self.player.alive(): self.draw_ui()

            if self.game_state == 'boss_fight':
                self.draw_boss_health_bar()

            if self.game_state in ['victory', 'game_over']:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 128)); self.screen.blit(overlay, (0, 0))
                if self.game_state == 'victory':
                    self.draw_text("VICTORY!", 80, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, GOLD)
                    if self.current_level == self.unlocked_levels - 1 and self.unlocked_levels <= len(ALL_LEVELS): self.draw_text(f"Level {self.unlocked_levels} Unlocked!", 40, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60)
                    self.draw_text("Press any key to continue", 30, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100)
                else:
                    self.draw_text("GAME OVER", 80, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, RED); self.draw_text("Press R to Restart Level", 30, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)
        
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("Paused", 80, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD)
            self.resume_button.draw(self.screen, pygame.mouse.get_pos())
            self.main_menu_button.draw(self.screen, pygame.mouse.get_pos())

        pygame.display.flip()

    def draw_ui(self):
        # Health bar
        health_rect = pygame.Rect(20, 20, 200, 25)
        pygame.draw.rect(self.screen, RED, health_rect)
        
        current_health_width = (self.player.health / self.player.max_health) * 200
        current_health_rect = pygame.Rect(20, 20, current_health_width, 25)
        pygame.draw.rect(self.screen, GREEN, current_health_rect)
        
        self.draw_text(f"Health: {self.player.health}", 24, 120, 32)
        
        # Coins
        self.draw_text(f"Coins: {self.player.coins}", 30, SCREEN_WIDTH - 100, 30, GOLD)
        
        # Current Weapon
        current_weapon_name = self.player.unlocked_weapons[self.player.current_weapon_index].replace('_', ' ').title()
        self.draw_text(f"Weapon: {current_weapon_name}", 30, SCREEN_WIDTH - 100, 60, WHITE)

        # Ultimate Meter
        if self.player.ultimate_ready:
            self.draw_text("ULTIMATE READY!", 30, SCREEN_WIDTH / 2, 90, YELLOW)
        else:
            self.draw_text(f"Ultimate: {self.player.ultimate_meter}/{self.player.ultimate_max_meter}", 30, SCREEN_WIDTH / 2, 90, WHITE)

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