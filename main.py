import pygame
import cv2
from settings import *
from gesture_controller import HandGestureController
from sprites import Player, Boss, Projectile, BossProjectile, Ground

class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Cuphead Camera Controller")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'playing' # playing, victory, game_over

        self.gesture_controller = HandGestureController()
        self.cap = cv2.VideoCapture(0)

        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.boss_projectiles = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        
        self.player = Player(self.screen_width, self.screen_height)
        self.boss = Boss(self.screen_width, self.screen_height, self)
        self.ground = Ground(0, self.screen_height - 40, self.screen_width, 40)
        
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.boss)
        self.all_sprites.add(self.ground)
        self.boss_group.add(self.boss)
        self.player_group.add(self.player)
        self.ground_group.add(self.ground)

    def draw_boss_health_bar(self):
        if self.boss.alive():
            health_pct = self.boss.health / 100.0
            bar_width = 200
            bar_height = 20
            fill = health_pct * bar_width
            outline_rect = pygame.Rect(self.screen_width // 2 - bar_width // 2, 20, bar_width, bar_height)
            fill_rect = pygame.Rect(self.screen_width // 2 - bar_width // 2, 20, fill, bar_height)
            pygame.draw.rect(self.screen, RED, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

    def draw_player_health_bar(self):
        if self.player.alive():
            health_pct = self.player.health / 100.0
            bar_width = 150
            bar_height = 15
            fill = health_pct * bar_width
            outline_rect = pygame.Rect(10, self.screen_height - bar_height - 10, bar_width, bar_height)
            fill_rect = pygame.Rect(10, self.screen_height - bar_height - 10, fill, bar_height)
            pygame.draw.rect(self.screen, GREEN, fill_rect)
            pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

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

            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            frame = cv2.flip(frame, 1)
            actions, processed_frame = self.gesture_controller.get_gestures(frame)

            if self.game_state == 'playing':
                # Update
                self.player.update(actions.get('move_x'))
                self.boss.update()
                self.projectiles.update()
                self.boss_projectiles.update()

                # Player-ground collision
                ground_hits = pygame.sprite.spritecollide(self.player, self.ground_group, False)
                if ground_hits:
                    self.player.rect.bottom = ground_hits[0].rect.top
                    self.player.vy = 0
                    if actions.get('jump'):
                        self.player.jump()

                if actions['shoot']:
                    projectile = self.player.shoot()
                    self.all_sprites.add(projectile)
                    self.projectiles.add(projectile)
                
                if actions.get('dash'):
                    self.player.dash()
                
                # Player projectile collision with boss
                hits = pygame.sprite.groupcollide(self.boss_group, self.projectiles, False, True)
                for boss, projectiles_hit in hits.items():
                    for projectile in projectiles_hit:
                        boss.take_damage(10)

                # Boss projectile collision with player
                hits = pygame.sprite.groupcollide(self.player_group, self.boss_projectiles, False, True)
                for player, projectiles_hit in hits.items():
                    for projectile in projectiles_hit:
                        player.take_damage(25)
                        if player.health <= 0:
                            self.game_state = 'game_over'

            # Draw
            self.screen.fill(BLACK)
            
            # Display the camera feed
            processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            processed_frame_pygame = pygame.image.frombuffer(processed_frame_rgb.tostring(), processed_frame_rgb.shape[1::-1], "RGB")
            self.screen.blit(processed_frame_pygame, (0, 0))

            if self.game_state == 'playing':
                self.all_sprites.draw(self.screen)
                self.draw_boss_health_bar()
                self.draw_player_health_bar()
            elif self.game_state == 'victory':
                self.draw_text("YOU WIN!", 64, self.screen_width // 2, self.screen_height // 2)
            elif self.game_state == 'game_over':
                self.draw_text("GAME OVER", 64, self.screen_width // 2, self.screen_height // 2)

            pygame.display.flip()
            self.clock.tick(60)

        self.cap.release()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()