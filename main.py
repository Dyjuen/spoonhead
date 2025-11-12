import pygame
import cv2
import os
from settings import *
from gesture_controller import HandGestureController
from sprites import Player, Boss, Projectile, BossProjectile, Platform, Coin, Enemy, BossGate
from ui import Button

class Game:
    """Main game class with platformer and boss fight"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Initialize mixer
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        Projectile.load_images() # Load bullet animations
        pygame.display.set_caption("Cuphead-Style Platformer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'home_screen'  # home_screen, level_selection, platformer, boss_fight, victory, game_over

        # Load sound effects
        self.shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_PATH)

        # Gesture controller
        self.gesture_controller = HandGestureController()
        self.cap = cv2.VideoCapture(0)

        # Camera offset
        self.camera_x = 0
        
        # Load background
        self.bg_image = pygame.image.load(os.path.join("assets", "bg.jpg")).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.boss_bg_image = pygame.image.load(os.path.join("assets", "bg2.jpg")).convert()
        self.boss_bg_image = pygame.transform.scale(self.boss_bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # UI Buttons
        self.setup_buttons()

    def setup_buttons(self):
        """Create all UI buttons"""
        # Home screen buttons
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50,
            "Start Game", BLUE, PURPLE
        )
        self.quit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50,
            "Quit Game", RED, PURPLE
        )

        # Level selection buttons
        self.level1_button = Button(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 60,
            "Level 1 (Locked)", GRAY, GRAY
        )
        self.level2_button = Button(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60,
            "Level 2", GREEN, PURPLE
        )
        self.level3_button = Button(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60,
            "Level 3 (Locked)", GRAY, GRAY
        )
        self.back_button = Button(
            20, SCREEN_HEIGHT - 70, 150, 50, "Back", RED, PURPLE
        )

    def init_level(self):
        """Initialize platformer level"""
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.boss_gate_group = pygame.sprite.Group()
        
        # Create player
        self.player = Player(100, 400)
        self.all_sprites.add(self.player)
        self.player_group.add(self.player)
        
        # Create platforms - Level layout
        platform_data = [
            (0, 550, 400, 40), (500, 550, 300, 40), (900, 550, 400, 40),
            (1400, 550, 400, 40), (1900, 550, 500, 40), (200, 450, 150, 30),
            (450, 400, 120, 30), (650, 350, 150, 30), (900, 300, 120, 30),
            (1100, 350, 150, 30), (1350, 400, 120, 30), (1600, 450, 150, 30),
            (1850, 400, 120, 30), (300, 250, 100, 25), (700, 200, 100, 25),
            (1150, 220, 120, 25), (1500, 250, 100, 25),
        ]
        
        for x, y, w, h in platform_data:
            platform = Platform(x, y, w, h)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        
        # Create coins
        coin_positions = [
            (250, 400), (320, 400), (520, 420), (700, 300), (770, 300),
            (950, 250), (1170, 170), (1240, 170), (1400, 500), (1650, 400),
            (1900, 350), (2000, 350), (2100, 350), (2200, 500)
        ]
        
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.all_sprites.add(coin)
            self.coins.add(coin)
        
        # Create enemies
        enemy_positions = [
            (600, 520, 100), (1000, 520, 150), (1500, 520, 120),
            (800, 320, 80), (1200, 320, 100),
        ]
        
        for x, y, patrol in enemy_positions:
            enemy = Enemy(x, y, patrol)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
        
        # Create boss gate
        self.boss_gate = BossGate(2300, 490)
        self.all_sprites.add(self.boss_gate)
        self.boss_gate_group.add(self.boss_gate)
        
        self.boss = None
        self.game_state = 'platformer'

    def init_boss_fight(self):
        """Initialize boss fight"""
        self.game_state = 'boss_fight'
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        self.boss_gate_group.empty()
        self.camera_x = 0
        self.player.rect.center = (200, 400)
        self.player.vx = 0
        self.player.vy = 0
        
        ground = Platform(0, 500, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        
        self.boss = Boss(SCREEN_WIDTH // 2, 150, self)
        self.all_sprites.add(self.boss)
        self.boss_group.add(self.boss)

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        if self.camera_x < 0:
            self.camera_x = 0

    def draw_ui(self):
        if self.player.health > 0:
            health_pct = self.player.health / 100.0
            bar_width, bar_height = 200, 25
            fill = health_pct * bar_width
            outline_rect = pygame.Rect(20, 20, bar_width, bar_height)
            fill_rect = pygame.Rect(20, 20, fill, bar_height)
            pygame.draw.rect(self.screen, RED, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 3)
            font = pygame.font.Font(None, 24)
            text = font.render(f"HP: {int(self.player.health)}", True, WHITE)
            self.screen.blit(text, (25, 23))
        
        font = pygame.font.Font(None, 32)
        coin_text = font.render(f"Coins: {self.player.coins}", True, GOLD)
        self.screen.blit(coin_text, (20, 60))
        
        if self.game_state == 'boss_fight' and self.boss and self.boss.alive():
            health_pct = self.boss.health / self.boss.max_health
            bar_width, bar_height = 400, 30
            fill = health_pct * bar_width
            x = SCREEN_WIDTH // 2 - bar_width // 2
            outline_rect = pygame.Rect(x, 20, bar_width, bar_height)
            fill_rect = pygame.Rect(x, 20, fill, bar_height)
            pygame.draw.rect(self.screen, PURPLE, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 3)
            font = pygame.font.Font(None, 28)
            text = font.render("BOSS", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 60))
            self.screen.blit(text, text_rect)
            phase_text = font.render(f"Phase {self.boss.phase}", True, YELLOW)
            phase_rect = phase_text.get_rect(center=(SCREEN_WIDTH // 2, 85))
            self.screen.blit(phase_text, phase_rect)

    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_home_screen(self, mouse_pos):
        self.draw_text("Spoonhead", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, GOLD)
        self.start_button.draw(self.screen, mouse_pos)
        self.quit_button.draw(self.screen, mouse_pos)

    def draw_level_selection(self, mouse_pos):
        self.draw_text("Select a Level", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, GOLD)
        self.level1_button.draw(self.screen, mouse_pos)
        self.level2_button.draw(self.screen, mouse_pos)
        self.level3_button.draw(self.screen, mouse_pos)
        self.back_button.draw(self.screen, mouse_pos)

    def run(self):
        """Main game loop"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state in ['platformer', 'boss_fight', 'level_selection', 'victory', 'game_over']:
                            self.game_state = 'home_screen'
                        else: # home_screen
                            self.running = False
                    elif event.key == pygame.K_r and self.game_state in ['victory', 'game_over']:
                        self.game_state = 'platformer'
                        self.camera_x = 0
                        self.init_level()

                # Button clicks
                if self.game_state == 'home_screen':
                    if self.start_button.is_clicked(event):
                        self.game_state = 'level_selection'
                    elif self.quit_button.is_clicked(event):
                        self.running = False
                elif self.game_state == 'level_selection':
                    if self.level2_button.is_clicked(event):
                        self.init_level()
                    elif self.back_button.is_clicked(event):
                        self.game_state = 'home_screen'

            # --- Game Logic ---
            if self.game_state in ['platformer', 'boss_fight', 'victory', 'game_over']:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                frame = cv2.flip(frame, 1)
                actions, processed_frame = self.gesture_controller.get_gestures(frame)

                # Update logic
                if self.game_state == 'platformer':
                    self.player.update(actions.get('move_x'), self.platforms)
                    self.coins.update()
                    self.enemies.update()
                    self.projectiles.update()
                    if self.player.rect.top > SCREEN_HEIGHT + 100: self.game_state = 'game_over'
                    if actions.get('jump'): self.player.jump()
                    if actions['shoot']:
                        proj = self.player.shoot(actions.get('shoot_direction', 'horizontal'))
                        if proj:
                            self.all_sprites.add(proj)
                            self.projectiles.add(proj)
                            self.shoot_sound.play() # Play shooting sound
                    if actions.get('dash'): self.player.dash()
                    if pygame.sprite.spritecollide(self.player, self.coins, True): self.player.collect_coin()
                    if pygame.sprite.spritecollide(self.player, self.enemies, False):
                        self.player.take_damage(10)
                        if self.player.health <= 0: self.game_state = 'game_over'
                    for enemy in self.enemies:
                        if pygame.sprite.spritecollide(enemy, self.projectiles, True): enemy.take_damage(10)
                    if pygame.sprite.spritecollide(self.player, self.boss_gate_group, False): self.init_boss_fight()
                    self.update_camera()

                elif self.game_state == 'boss_fight':
                    self.player.update(actions.get('move_x'), self.platforms)
                    if self.boss: self.boss.update()
                    self.projectiles.update()
                    self.boss_projectiles.update()
                    if self.player.rect.top > SCREEN_HEIGHT + 100: self.game_state = 'game_over'
                    if actions.get('jump'): self.player.jump()
                    if actions['shoot']:
                        proj = self.player.shoot(actions.get('shoot_direction', 'horizontal'))
                        if proj:
                            self.all_sprites.add(proj)
                            self.projectiles.add(proj)
                            self.shoot_sound.play() # Play shooting sound

                    if actions.get('dash'): self.player.dash()
                    if self.boss and pygame.sprite.spritecollide(self.boss, self.projectiles, True): self.boss.take_damage(10)
                    if pygame.sprite.spritecollide(self.player, self.boss_projectiles, True):
                        self.player.take_damage(25)
                        if self.player.health <= 0: self.game_state = 'game_over'

            # --- Drawing ---
            # Draw background based on game state
            if self.game_state in ['boss_fight', 'victory']:
                self.screen.blit(self.boss_bg_image, (0, 0))
            elif self.game_state == 'platformer':
                self.screen.blit(self.bg_image, (0, 0))
            else: # Home, level selection, game over
                self.screen.blit(self.bg_image, (0, 0))


            if self.game_state == 'home_screen':
                self.draw_home_screen(mouse_pos)
            elif self.game_state == 'level_selection':
                self.draw_level_selection(mouse_pos)
            elif self.game_state in ['platformer', 'boss_fight', 'victory', 'game_over']:
                if self.game_state == 'platformer':
                    # Draw sprites with camera offset
                    for sprite in self.all_sprites:
                        self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
                else: # boss_fight, victory, game_over
                    self.all_sprites.draw(self.screen)
                
                self.draw_ui()
                
                small_frame = cv2.resize(processed_frame, (240, 180))
                processed_frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                processed_frame_pygame = pygame.image.frombuffer(
                    processed_frame_rgb.tobytes(), processed_frame_rgb.shape[1::-1], "RGB"
                )
                self.screen.blit(processed_frame_pygame, (SCREEN_WIDTH - 250, 10))

                if self.game_state == 'victory':
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))
                    self.screen.blit(overlay, (0, 0))
                    self.draw_text("VICTORY!", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, GOLD)
                    self.draw_text(f"Coins Collected: {self.player.coins}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
                    self.draw_text("Press R to Restart | ESC to Home", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
                
                elif self.game_state == 'game_over':
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))
                    self.screen.blit(overlay, (0, 0))
                    self.draw_text("GAME OVER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, RED)
                    self.draw_text("Press R to Restart | ESC to Home", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)

            pygame.display.flip()
            self.clock.tick(60)

        self.cap.release()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()