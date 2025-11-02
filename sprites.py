import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    """Player character"""
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        if PLAYER_IMAGE:
            self.image = pygame.image.load(PLAYER_IMAGE).convert_alpha()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(WHITE) # White square
        
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 100))
        self.health = 100
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.gravity = 0.5
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 200 # ms
        self.dash_speed = 15

    def update(self, move_x):
        # Horizontal Movement
        self.vx = 0
        if move_x is not None:
            if move_x < 0.4:
                self.vx = -self.speed
            elif move_x > 0.6:
                self.vx = self.speed

        if self.dashing:
            now = pygame.time.get_ticks()
            if now - self.dash_timer > self.dash_duration:
                self.dashing = False
            self.rect.x += self.vx * self.dash_speed # Apply dash speed
        else:
            self.rect.x += self.vx

        # Gravity
        self.vy += self.gravity
        self.rect.y += self.vy
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width

    def jump(self):
        self.vy = -15

    def dash(self):
        if not self.dashing:
            self.dashing = True
            self.dash_timer = pygame.time.get_ticks()

    def shoot(self):
        return Projectile(self.rect.centerx, self.rect.top)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

class Projectile(pygame.sprite.Sprite):
    """Projectile shot by the player"""
    def __init__(self, x, y):
        super().__init__()
        if PROJECTILE_IMAGE:
            self.image = pygame.image.load(PROJECTILE_IMAGE).convert_alpha()
        else:
            self.image = pygame.Surface((10, 20))
            self.image.fill(RED) # Red rectangle
        
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    """Boss character"""
    def __init__(self, screen_width, screen_height, game):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        
        if BOSS_IMAGE:
            self.image = pygame.image.load(BOSS_IMAGE).convert_alpha()
        else:
            self.image = pygame.Surface((100, 100))
            self.image.fill(GREEN) # Green square
        
        self.rect = self.image.get_rect(center=(screen_width // 2, 100))
        self.health = 100
        self.speed = 5
        self.shoot_delay = 1000 # milliseconds
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > self.screen_width:
            self.speed = -self.speed
        self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            projectile = BossProjectile(self.rect.centerx, self.rect.bottom, self.screen_height)
            self.game.all_sprites.add(projectile)
            self.game.boss_projectiles.add(projectile)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            self.game.game_state = 'victory'

class BossProjectile(pygame.sprite.Sprite):
    """Projectile shot by the boss"""
    def __init__(self, x, y, screen_height):
        super().__init__()
        self.screen_height = screen_height
        self.image = pygame.Surface((10, 20))
        self.image.fill(YELLOW) # Yellow rectangle
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 5
        if self.rect.top > self.screen_height:
            self.kill()

class Ground(pygame.sprite.Sprite):
    """Ground platform"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
