import pygame
import os
import json
from settings import *
from controller import XboxController
from sprites import Player, Boss, Projectile, BossProjectile, Platform, MovingPlatform, Coin, Enemy, BossGate, EnemyProjectile
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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        Projectile.load_images()
        pygame.display.set_caption("Spoonhead")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'home_screen'

        self.unlocked_levels = 1
        self.total_coins = 0
        self.upgrades = {item_id: False for item_id in SHOP_ITEMS}
        self.current_level = 0
        self.load_game_data()

        self.controller = XboxController()
        self.camera_x = 0
        self.player = None
        
        self.load_assets()
        self.setup_buttons()
        self.shop_screen = ShopScreen(self.screen, self.total_coins, self.upgrades, SHOP_ITEMS)

    def load_game_data(self):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                self.unlocked_levels = data.get('unlocked_levels', 1)
                self.total_coins = data.get('total_coins', 0)
                loaded_upgrades = data.get('upgrades', {})
                for item_id in SHOP_ITEMS:
                    if item_id in loaded_upgrades:
                        self.upgrades[item_id] = loaded_upgrades[item_id]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Save file not found, starting new game.")
            self.upgrades = {item_id: False for item_id in SHOP_ITEMS}

    def save_game_data(self):
        data = {'unlocked_levels': self.unlocked_levels, 'total_coins': self.total_coins, 'upgrades': self.upgrades}
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)

    def load_assets(self):
        try:
            self.bg_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.jpg")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.boss_bg_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg2.jpg")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print("Warning: Background images not found.")
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.bg_image.fill(SKY_BLUE)
            self.boss_bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.boss_bg_image.fill(DARK_GRAY)

    def setup_buttons(self):
        self.start_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 50, "Start Game", BLUE, PURPLE)
        self.quit_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 50, "Quit Game", RED, PURPLE)
        
        self.level_buttons = []
        for i in range(1, len(ALL_LEVELS) + 1):
            y_pos = SCREEN_HEIGHT/2 - 100 + (i-1)*80
            self.level_buttons.append(Button(SCREEN_WIDTH/2 - 150, y_pos, 300, 60, f"Level {i}", GREEN, PURPLE))

        self.shop_button = Button(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 70, 150, 50, "Shop", GOLD, PURPLE)
        self.back_button = Button(20, SCREEN_HEIGHT - 70, 150, 50, "Back", RED, PURPLE)

    def init_level(self, level_number):
        self.current_level = level_number; level_data = ALL_LEVELS[level_number]
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group(); self.enemy_projectiles = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group(); self.boss_group = pygame.sprite.Group()
        self.boss_gate_group = pygame.sprite.Group()
        
        self.player = Player(100, 400, self.upgrades)
        self.all_sprites.add(self.player)
        
        for p_data in level_data["platforms"]: self.platforms.add(Platform(*p_data))
        for p_data in level_data["moving_platforms"]:
            p = MovingPlatform(*p_data); self.platforms.add(p); self.moving_platforms.add(p)
        for c_data in level_data["coins"]: self.coins.add(Coin(*c_data))
        for e_data in level_data["enemies"]: self.enemies.add(Enemy(**e_data))
        
        self.boss_gate = BossGate(level_data["boss_gate_x"], 460)
        self.boss_gate_group.add(self.boss_gate)
        
        # Explicitly add all sprites to the main group
        self.all_sprites.add(self.player)
        for platform in self.platforms:
            self.all_sprites.add(platform)
        for coin in self.coins:
            self.all_sprites.add(coin)
        for enemy in self.enemies:
            self.all_sprites.add(enemy)
        self.all_sprites.add(self.boss_gate)
        
        self.boss = None; self.game_state = 'platformer'; self.camera_x = 0

    def init_boss_fight(self):
        self.game_state = 'boss_fight'
        level_data = ALL_LEVELS[self.current_level]
        boss_data = level_data["boss"].copy()
        for sprite in self.all_sprites:
            if sprite != self.player: sprite.kill()
        self.platforms.empty(); self.coins.empty(); self.enemies.empty(); self.boss_gate_group.empty()
        self.camera_x = 0; self.player.rect.center = (200, 400)
        
        ground = Platform(0, 500, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground); self.platforms.add(ground)
        
        self.boss = Boss(
            x=SCREEN_WIDTH * 0.75,
            y=SCREEN_HEIGHT / 2,
            game=self,
            health=boss_data['health'],
            speed=boss_data['speed'],
            shoot_interval=boss_data['shoot_interval'],
            phases=boss_data['phases'],
            boss_type=boss_data['boss_type']
        )
        self.all_sprites.add(self.boss); self.boss_group.add(self.boss)

    def draw_text(self, text, size, x, y, color=WHITE, align="center"):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center": text_rect.center = (x, y)
        elif align == "topleft": text_rect.topleft = (x, y)
        elif align == "topright": text_rect.topright = (x, y)
        self.screen.blit(text_surface, text_rect)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): self.running = False
            
            if self.game_state == 'victory':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: self.game_state = 'level_selection'
            elif self.game_state == 'game_over':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.init_level(self.current_level)
            elif self.game_state == 'home_screen':
                if self.start_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                elif self.quit_button.is_clicked(event, mouse_pos): self.running = False
            elif self.game_state == 'level_selection':
                if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'home_screen'
                if self.shop_button.is_clicked(event, mouse_pos): self.game_state = 'shop_screen'
                for i, button in enumerate(self.level_buttons):
                    if i < self.unlocked_levels and button.is_clicked(event, mouse_pos): self.init_level(i + 1)
            elif self.game_state == 'shop_screen':
                if self.back_button.is_clicked(event, mouse_pos): self.game_state = 'level_selection'
                
                purchased_item = self.shop_screen.handle_event(event)
                if purchased_item:
                    item_data = SHOP_ITEMS[purchased_item]
                    if self.total_coins >= item_data['price']:
                        self.total_coins -= item_data['price']
                        self.upgrades[purchased_item] = True
                        self.save_game_data()
                        # Update the shop screen to reflect the change
                        self.shop_screen.total_coins = self.total_coins
                        self.shop_screen.upgrades = self.upgrades


    def update_game_state(self):
        if self.player and self.player.health <= 0: self.game_state = 'game_over'
        if self.game_state in ['victory', 'game_over', 'home_screen', 'level_selection', 'shop_screen']: return

        actions = self.controller.get_actions()
        if actions.get('jump'): self.player.jump()
        if actions.get('dash'): self.player.dash()
        if actions.get('shoot'):
            projectiles = self.player.shoot(actions.get('shoot_direction', 'horizontal'))
            if projectiles: self.all_sprites.add(projectiles); self.projectiles.add(projectiles)

        self.player.update(actions.get('move_x'), self.platforms)
        self.projectiles.update()
        if self.game_state == 'platformer':
            self.moving_platforms.update(); self.enemies.update(self.player, self.all_sprites, self.enemy_projectiles)
            self.enemy_projectiles.update(); self.coins.update()
        elif self.game_state == 'boss_fight' and self.boss:
            self.boss.update(); self.boss_projectiles.update()
        
        if self.player.rect.top > SCREEN_HEIGHT + 200: self.game_state = 'game_over'

        if self.game_state == 'platformer':
            collected = pygame.sprite.spritecollide(self.player, self.coins, True)
            if collected: self.player.coins += len(collected)
            if pygame.sprite.spritecollide(self.player, self.enemies, False): self.player.take_damage(10)
            if pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True): self.player.take_damage(15)
            
            # Manual collision check to replace groupcollide
            for proj in self.projectiles:
                hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False)
                if hit_enemies:
                    proj.kill() # Kill the projectile
                    for enemy in hit_enemies:
                        enemy.take_damage(10) # Damage each enemy it hit

            if pygame.sprite.spritecollide(self.player, self.boss_gate_group, False): self.init_boss_fight() # <-- THE LINE
            self.update_camera()
        elif self.game_state == 'boss_fight':
            if self.boss and pygame.sprite.spritecollide(self.boss, self.projectiles, True): self.boss.take_damage(10)
            if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True): self.player.take_damage(25)
        
        if self.boss and not self.boss.alive() and self.game_state == 'boss_fight':
            self.game_state = 'victory'; self.total_coins += self.player.coins
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
        current_bg = self.boss_bg_image if self.game_state in ['boss_fight', 'victory'] else self.bg_image
        self.screen.blit(current_bg, (0, 0))

        if self.game_state == 'home_screen':
            self.draw_text("Spoonhead", 100, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, GOLD); self.start_button.draw(self.screen, pygame.mouse.get_pos()); self.quit_button.draw(self.screen, pygame.mouse.get_pos())
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

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(60)
        self.save_game_data()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()