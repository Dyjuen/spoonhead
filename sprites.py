import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    """Player character with platformer mechanics"""
    def __init__(self, x, y):
        super().__init__()
        
        if PLAYER_IMAGE:
            self.image = pygame.image.load(PLAYER_IMAGE).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(WHITE)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 100
        self.vx = 0
        self.vy = 0
        self.speed = 6
        self.jump_power = -16
        self.gravity = 0.8
        self.on_ground = False
        self.facing_right = True
        
        # Dash mechanics
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 200
        self.dash_speed = 15
        self.dash_cooldown = 500
        self.last_dash = 0
        
        # Shooting mechanics
        self.can_shoot = True
        self.shoot_cooldown = 250
        self.last_shot = 0
        
        # Coins collected
        self.coins = 0

    def update(self, move_x, platforms):
        current_time = pygame.time.get_ticks()
        
        # Horizontal Movement
        self.vx = 0
        if move_x is not None:
            if move_x < 0.4:
                self.vx = -self.speed
                self.facing_right = False
            elif move_x > 0.6:
                self.vx = self.speed
                self.facing_right = True

        # Apply dash
        if self.dashing:
            if current_time - self.dash_timer > self.dash_duration:
                self.dashing = False
            else:
                self.vx *= self.dash_speed / self.speed

        self.rect.x += self.vx

        # Check horizontal collisions
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platform_hits:
            if self.vx > 0:  # Moving right
                self.rect.right = platform.rect.left
            elif self.vx < 0:  # Moving left
                self.rect.left = platform.rect.right

        # Vertical movement (gravity)
        self.vy += self.gravity
        if self.vy > 15:  # Terminal velocity
            self.vy = 15
        
        self.rect.y += self.vy
        self.on_ground = False

        # Check vertical collisions
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platform_hits:
            if self.vy > 0:  # Falling down
                self.rect.bottom = platform.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:  # Jumping up
                self.rect.top = platform.rect.bottom
                self.vy = 0

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

    def dash(self):
        current_time = pygame.time.get_ticks()
        if not self.dashing and current_time - self.last_dash > self.dash_cooldown:
            self.dashing = True
            self.dash_timer = current_time
            self.last_dash = current_time

    def shoot(self, shoot_direction='horizontal'):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.last_shot = current_time
            direction = 1 if self.facing_right else -1
            return Projectile(self.rect.centerx, self.rect.centery, direction, shoot_direction)
        return None

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def collect_coin(self):
        self.coins += 1


class Projectile(pygame.sprite.Sprite):
    """Projectile shot by the player with directional support"""
    def __init__(self, x, y, direction=1, shoot_direction='horizontal'):
        super().__init__()
        if PROJECTILE_IMAGE:
            self.image = pygame.image.load(PROJECTILE_IMAGE).convert_alpha()
        else:
            self.image = pygame.Surface((15, 8))
            self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.shoot_direction = shoot_direction
        
        # Set velocity based on shoot direction
        if shoot_direction == 'up':
            self.vx = 0
            self.vy = -12
        elif shoot_direction == 'down':
            self.vx = 0
            self.vy = 12
        elif shoot_direction == 'up_right':
            self.vx = 8 * direction
            self.vy = -8
        elif shoot_direction == 'up_left':
            self.vx = -8 * abs(direction)
            self.vy = -8
        else:  # horizontal
            self.vx = 12 * direction
            self.vy = 0

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Remove if off screen
        if (self.rect.right < -100 or self.rect.left > 2000 or
            self.rect.bottom < -100 or self.rect.top > 1000):
            self.kill()


class Platform(pygame.sprite.Sprite):
    """Platform for player to walk on"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        # Add some visual detail
        pygame.draw.rect(self.image, (101, 67, 33), (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(pygame.sprite.Sprite):
    """Collectible coin"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        pygame.draw.circle(self.image, GOLD, (10, 10), 10)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 8)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset = random.uniform(0, 6.28)
        self.bob_range = 5
        self.original_y = y

    def update(self):
        # Bobbing animation
        import math
        self.bob_offset += 0.1
        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range)


class Enemy(pygame.sprite.Sprite):
    """Basic enemy that patrols"""
    def __init__(self, x, y, patrol_distance=200):
        super().__init__()
        if ENEMY_IMAGE:
            self.image = pygame.image.load(ENEMY_IMAGE).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        else:
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 30
        self.speed = 2
        self.direction = 1
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.damage = 20

    def update(self):
        # Patrol movement
        self.rect.x += self.speed * self.direction
        
        # Turn around at patrol boundaries
        if abs(self.rect.centerx - self.start_x) > self.patrol_distance:
            self.direction *= -1

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()


class BossGate(pygame.sprite.Sprite):
    """Gate that triggers boss fight"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 120))
        self.image.fill(PURPLE)
        # Draw gate design
        pygame.draw.rect(self.image, (138, 43, 226), (10, 10, 60, 100), 5)
        pygame.draw.rect(self.image, (75, 0, 130), (20, 20, 40, 80))
        self.rect = self.image.get_rect(center=(x, y))


class Boss(pygame.sprite.Sprite):
    """Boss character with multiple phases"""
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        
        if BOSS_IMAGE:
            self.image = pygame.image.load(BOSS_IMAGE).convert_alpha()
            self.image = pygame.transform.scale(self.image, (120, 120))
        else:
            self.image = pygame.Surface((120, 120))
            self.image.fill(PURPLE)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 200
        self.max_health = 200
        self.speed = 3
        self.direction = 1
        
        # Attack patterns
        self.shoot_delay = 1500
        self.last_shot = pygame.time.get_ticks()
        self.phase = 1
        
        # Movement boundaries
        self.min_x = 100
        self.max_x = 700

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Phase transitions
        health_percentage = self.health / self.max_health
        if health_percentage < 0.5 and self.phase == 1:
            self.phase = 2
            self.shoot_delay = 1000  # Faster shooting
        elif health_percentage < 0.25 and self.phase == 2:
            self.phase = 3
            self.shoot_delay = 700  # Even faster
        
        # Movement
        self.rect.x += self.speed * self.direction
        if self.rect.left < self.min_x or self.rect.right > self.max_x:
            self.direction *= -1
        
        # Shooting
        if current_time - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        if self.phase == 1:
            # Single projectile downward
            projectile = BossProjectile(self.rect.centerx, self.rect.bottom, 0, 6)
            self.game.all_sprites.add(projectile)
            self.game.boss_projectiles.add(projectile)
        elif self.phase == 2:
            # Three projectiles spread
            for angle in [-0.3, 0, 0.3]:
                projectile = BossProjectile(self.rect.centerx, self.rect.bottom, angle * 5, 6)
                self.game.all_sprites.add(projectile)
                self.game.boss_projectiles.add(projectile)
        else:
            # Five projectiles wide spread
            for angle in [-0.5, -0.25, 0, 0.25, 0.5]:
                projectile = BossProjectile(self.rect.centerx, self.rect.bottom, angle * 7, 7)
                self.game.all_sprites.add(projectile)
                self.game.boss_projectiles.add(projectile)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            self.game.game_state = 'victory'


class BossProjectile(pygame.sprite.Sprite):
    """Projectile shot by the boss"""
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        pygame.draw.circle(self.image, RED, (7, 7), 7)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Remove if way off screen
        if (self.rect.top > 1000 or self.rect.bottom < -100 or 
            self.rect.right < -100 or self.rect.left > 2000):
            self.kill()