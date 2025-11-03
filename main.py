import pygame
import cv2
from settings import *
from gesture_controller import HandGestureController
from sprites import Player, Boss, Projectile, BossProjectile, Platform, Coin, Enemy, BossGate

class Game:
    """Main game class with platformer and boss fight"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cuphead-Style Platformer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'platformer'  # platformer, boss_fight, victory, game_over

        # Gesture controller
        self.gesture_controller = HandGestureController()
        self.cap = cv2.VideoCapture(0)

        # Camera offset
        self.camera_x = 0
        
        # Initialize level
        self.init_level()

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
            # Ground platforms
            (0, 550, 400, 40),
            (500, 550, 300, 40),
            (900, 550, 400, 40),
            (1400, 550, 400, 40),
            (1900, 550, 500, 40),
            
            # Middle platforms
            (200, 450, 150, 30),
            (450, 400, 120, 30),
            (650, 350, 150, 30),
            (900, 300, 120, 30),
            (1100, 350, 150, 30),
            (1350, 400, 120, 30),
            (1600, 450, 150, 30),
            (1850, 400, 120, 30),
            
            # High platforms
            (300, 250, 100, 25),
            (700, 200, 100, 25),
            (1150, 220, 120, 25),
            (1500, 250, 100, 25),
        ]
        
        for x, y, w, h in platform_data:
            platform = Platform(x, y, w, h)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        
        # Create coins
        coin_positions = [
            (250, 400), (320, 400), (520, 420),
            (700, 300), (770, 300), (950, 250),
            (1170, 170), (1240, 170), (1400, 500),
            (1650, 400), (1900, 350), (2000, 350),
            (2100, 350), (2200, 500)
        ]
        
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.all_sprites.add(coin)
            self.coins.add(coin)
        
        # Create enemies
        enemy_positions = [
            (600, 520, 100),
            (1000, 520, 150),
            (1500, 520, 120),
            (800, 320, 80),
            (1200, 320, 100),
        ]
        
        for x, y, patrol in enemy_positions:
            enemy = Enemy(x, y, patrol)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
        
        # Create boss gate at end
        self.boss_gate = BossGate(2300, 490)
        self.all_sprites.add(self.boss_gate)
        self.boss_gate_group.add(self.boss_gate)
        
        self.boss = None

    def init_boss_fight(self):
        """Initialize boss fight"""
        self.game_state = 'boss_fight'
        
        # Clear platformer sprites except player
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        self.boss_gate_group.empty()
        
        # Reset camera
        self.camera_x = 0
        
        # Position player
        self.player.rect.center = (200, 400)
        self.player.vx = 0
        self.player.vy = 0
        
        # Create boss arena - simple floor
        ground = Platform(0, 500, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        
        # Create boss
        self.boss = Boss(SCREEN_WIDTH // 2, 150, self)
        self.all_sprites.add(self.boss)
        self.boss_group.add(self.boss)

    def update_camera(self):
        """Update camera to follow player"""
        # Camera follows player with some lag
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # Clamp camera
        if self.camera_x < 0:
            self.camera_x = 0

    def draw_ui(self):
        """Draw game UI"""
        # Health bar
        if self.player.health > 0:
            health_pct = self.player.health / 100.0
            bar_width = 200
            bar_height = 25
            fill = health_pct * bar_width
            outline_rect = pygame.Rect(20, 20, bar_width, bar_height)
            fill_rect = pygame.Rect(20, 20, fill, bar_height)
            pygame.draw.rect(self.screen, RED, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 3)
            
            # Health text
            font = pygame.font.Font(None, 24)
            text = font.render(f"HP: {int(self.player.health)}", True, WHITE)
            self.screen.blit(text, (25, 23))
        
        # Coin counter
        font = pygame.font.Font(None, 32)
        coin_text = font.render(f"Coins: {self.player.coins}", True, GOLD)
        self.screen.blit(coin_text, (20, 60))
        
        # Boss health bar (if in boss fight)
        if self.game_state == 'boss_fight' and self.boss and self.boss.alive():
            health_pct = self.boss.health / self.boss.max_health
            bar_width = 400
            bar_height = 30
            fill = health_pct * bar_width
            x = SCREEN_WIDTH // 2 - bar_width // 2
            outline_rect = pygame.Rect(x, 20, bar_width, bar_height)
            fill_rect = pygame.Rect(x, 20, fill, bar_height)
            pygame.draw.rect(self.screen, PURPLE, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 3)
            
            # Boss name
            font = pygame.font.Font(None, 28)
            text = font.render("BOSS", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 60))
            self.screen.blit(text, text_rect)
            
            # Phase indicator
            phase_text = font.render(f"Phase {self.boss.phase}", True, YELLOW)
            phase_rect = phase_text.get_rect(center=(SCREEN_WIDTH // 2, 85))
            self.screen.blit(phase_text, phase_rect)

    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Get camera frame and gestures
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            frame = cv2.flip(frame, 1)
            actions, processed_frame = self.gesture_controller.get_gestures(frame)

            if self.game_state == 'platformer':
                # Update
                self.player.update(actions.get('move_x'), self.platforms)
                self.coins.update()
                self.enemies.update()
                self.projectiles.update()
                
                # Jump
                if actions.get('jump'):
                    self.player.jump()
                
                # Shoot
                if actions['shoot']:
                    projectile = self.player.shoot()
                    if projectile:
                        self.all_sprites.add(projectile)
                        self.projectiles.add(projectile)
                
                # Dash
                if actions.get('dash'):
                    self.player.dash()
                
                # Coin collection
                coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
                for coin in coin_hits:
                    self.player.collect_coin()
                
                # Enemy collision
                enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
                for enemy in enemy_hits:
                    self.player.take_damage(enemy.damage)
                    enemy.rect.x += 50 * (-1 if enemy.direction > 0 else 1)
                    if self.player.health <= 0:
                        self.game_state = 'game_over'
                
                # Projectile hits enemy
                for enemy in self.enemies:
                    hits = pygame.sprite.spritecollide(enemy, self.projectiles, True)
                    if hits:
                        enemy.take_damage(10)
                
                # Check boss gate
                gate_hit = pygame.sprite.spritecollide(self.player, self.boss_gate_group, False)
                if gate_hit:
                    self.init_boss_fight()
                
                # Update camera
                self.update_camera()

            elif self.game_state == 'boss_fight':
                # Update
                self.player.update(actions.get('move_x'), self.platforms)
                if self.boss:
                    self.boss.update()
                self.projectiles.update()
                self.boss_projectiles.update()
                
                # Jump
                if actions.get('jump'):
                    self.player.jump()
                
                # Shoot
                if actions['shoot']:
                    projectile = self.player.shoot()
                    if projectile:
                        self.all_sprites.add(projectile)
                        self.projectiles.add(projectile)
                
                # Dash
                if actions.get('dash'):
                    self.player.dash()
                
                # Player projectile hits boss
                if self.boss:
                    hits = pygame.sprite.spritecollide(self.boss, self.projectiles, True)
                    for hit in hits:
                        self.boss.take_damage(10)
                
                # Boss projectile hits player
                hits = pygame.sprite.spritecollide(self.player, self.boss_projectiles, True)
                for hit in hits:
                    self.player.take_damage(25)
                    if self.player.health <= 0:
                        self.game_state = 'game_over'

            # Draw
            self.screen.fill(SKY_BLUE)
            
            # Draw sprites with camera offset
            if self.game_state == 'platformer':
                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
            else:
                self.all_sprites.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            # Draw camera feed in corner
            small_frame = cv2.resize(processed_frame, (240, 180))
            processed_frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            processed_frame_pygame = pygame.image.frombuffer(
                processed_frame_rgb.tobytes(), 
                processed_frame_rgb.shape[1::-1], 
                "RGB"
            )
            self.screen.blit(processed_frame_pygame, (SCREEN_WIDTH - 250, 10))
            
            # Draw game state overlays
            if self.game_state == 'victory':
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                self.draw_text("VICTORY!", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, GOLD)
                self.draw_text(f"Coins Collected: {self.player.coins}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
                self.draw_text("Press ESC to quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
            
            elif self.game_state == 'game_over':
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                self.draw_text("GAME OVER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, RED)
                self.draw_text("Press ESC to quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)

            pygame.display.flip()
            self.clock.tick(60)

        self.cap.release()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()