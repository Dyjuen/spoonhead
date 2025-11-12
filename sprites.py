import pygame
import random
import os
import math
from settings import *

class SpriteSheet:
    """Utility for loading and parsing sprite sheets."""
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        """Extracts a single image from the sprite sheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_animation_frames(self, frame_width, frame_height):
        """Extracts frames from a horizontal animation strip."""
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        for x in range(0, sheet_width, frame_width):
            frame = self.get_image(x, 0, frame_width, self.sprite_sheet.get_height())
            frames.append(frame)
        return frames

class Player(pygame.sprite.Sprite):
    """Player character with platformer mechanics and animations."""
    def __init__(self, x, y):
        super().__init__()
        
        self.load_animations()
        self.action = 'idle'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.health = 100
        self.vx = 0
        self.vy = 0
        self.speed = 6
        self.jump_power = -16
        self.gravity = 0.8
        self.on_ground = False
        self.facing_right = True
        
        self.jumps_left = 2
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 200
        self.dash_speed = 15
        self.dash_cooldown = 500
        self.last_dash = 0
        
        self.can_shoot = True
        self.shoot_cooldown = 250
        self.last_shot = 0
        
        self.coins = 0

    def load_animations(self):
        """Load all player animations from sprite sheets."""
        self.animations = {'idle': [], 'run': [], 'jump': [], 'double_jump': []}
        player_size = (72, 72)

        for anim_type, sprite_path in [
            ('idle', PLAYER_IDLE_SPRITE), ('run', PLAYER_RUN_SPRITE),
            ('jump', PLAYER_JUMP_SPRITE), ('double_jump', PLAYER_DOUBLE_JUMP_SPRITE)
        ]:
            sheet = SpriteSheet(sprite_path)
            frames = sheet.get_animation_frames(48, 48)
            scaled_frames = [pygame.transform.scale(frame, player_size) for frame in frames]
            self.animations[anim_type] = scaled_frames

    def animate(self):
        """Handles the animation logic."""
        now = pygame.time.get_ticks()
        animation_speed = 100

        if self.action == 'double_jump' and self.frame_index < len(self.animations['double_jump']) - 1:
            animation_speed = 80
        elif self.action == 'double_jump' and self.frame_index >= len(self.animations['double_jump']) - 1:
            self.set_action('jump')

        if now - self.last_frame_update > animation_speed:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.action])
            
            new_image = self.animations[self.action][self.frame_index]
            if not self.facing_right:
                new_image = pygame.transform.flip(new_image, True, False)
            
            center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect(center=center)

    def set_action(self, new_action):
        """Change the player's current animation action."""
        if self.action != new_action:
            self.action = new_action
            self.frame_index = 0

    def update(self, move_x, platforms):
        current_time = pygame.time.get_ticks()
        
        if not self.on_ground:
            if self.action not in ['jump', 'double_jump']: self.set_action('jump')
        elif move_x is not None and (move_x < 0.4 or move_x > 0.6): self.set_action('run')
        else: self.set_action('idle')

        self.vx = 0
        if move_x is not None:
            if move_x < 0.4: self.vx = -self.speed; self.facing_right = False
            elif move_x > 0.6: self.vx = self.speed; self.facing_right = True

        if self.dashing:
            if current_time - self.dash_timer > self.dash_duration: self.dashing = False
            else: self.vx *= self.dash_speed / self.speed

        self.rect.x += self.vx
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.vx > 0: self.rect.right = platform.rect.left
            elif self.vx < 0: self.rect.left = platform.rect.right

        self.vy += self.gravity
        if self.vy > 15: self.vy = 15
        self.rect.y += self.vy
        self.on_ground = False

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.vy > 0:
                self.rect.bottom = platform.rect.top
                self.vy = 0
                self.on_ground = True
                self.jumps_left = 2
            elif self.vy < 0:
                self.rect.top = platform.rect.bottom
                self.vy = 0
        
        self.animate()

    def jump(self):
        if self.jumps_left > 0:
            if self.jumps_left == 1: self.set_action('double_jump')
            else: self.set_action('jump')
            self.vy = self.jump_power
            self.on_ground = False
            self.jumps_left -= 1

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
        if self.health <= 0: self.health = 0

    def collect_coin(self):
        self.coins += 1

class Projectile(pygame.sprite.Sprite):
    """Animated projectile shot by the player."""
    animation_frames_right = []
    animation_frames_left = []

    @staticmethod
    def load_images():
        """Load and scale projectile images once."""
        if Projectile.animation_frames_right: return
            
        bullet_size = (20, 10)
        sprite_paths = [os.path.join("assets", "Bullets", "7_1.png"), os.path.join("assets", "Bullets", "7_2.png")]
        
        for path in sprite_paths:
            image = pygame.image.load(path).convert_alpha()
            scaled_image = pygame.transform.scale(image, bullet_size)
            Projectile.animation_frames_right.append(scaled_image)
            flipped_image = pygame.transform.flip(scaled_image, True, False)
            Projectile.animation_frames_left.append(flipped_image)

    def __init__(self, x, y, direction=1, shoot_direction='horizontal'):
        super().__init__()
        
        self.direction = direction
        self.anim_frames = Projectile.animation_frames_right if direction == 1 else Projectile.animation_frames_left
        
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.anim_frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.shoot_direction = shoot_direction
        
        if shoot_direction == 'up': self.vx, self.vy = 0, -12
        elif shoot_direction == 'down': self.vx, self.vy = 0, 12
        elif shoot_direction == 'up_right': self.vx, self.vy = 8 * direction, -8
        elif shoot_direction == 'up_left': self.vx, self.vy = -8 * abs(direction), -8
        else: self.vx, self.vy = 12 * direction, 0

    def animate(self):
        """Cycle through the projectile animation."""
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 100:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.anim_frames)
            center = self.rect.center
            self.image = self.anim_frames[self.frame_index]
            self.rect = self.image.get_rect(center=center)

    def update(self):
        self.animate()
        self.rect.x += self.vx
        self.rect.y += self.vy
        if not (-100 < self.rect.right and self.rect.left < 2000 and \
                -100 < self.rect.bottom and self.rect.top < 1000):
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height)); self.image.fill(BROWN)
        pygame.draw.rect(self.image, (101, 67, 33), (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset = random.uniform(0, 6.28); self.bob_range = 5
        self.original_y = y

    def update(self):
        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range)
        self.bob_offset += 0.1

class Enemy(pygame.sprite.Sprite):
    """Basic enemy that patrols with animations and flash effect."""
    def __init__(self, x, y, patrol_distance=200):
        super().__init__()
        
        self.load_animations()
        self.action = 'walk'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.health = 30
        self.speed = 2
        self.direction = 1
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.damage = 20

        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 150 # ms

    def load_animations(self):
        """Load all enemy animations and create flash versions."""
        self.animations = {'walk': []}
        self.flash_animations = {'walk': []}
        enemy_size = (64, 64)
        
        sheet = SpriteSheet(ENEMY_WALK_SPRITE)
        frames = sheet.get_animation_frames(48, 48) 
        
        for frame in frames:
            scaled_frame = pygame.transform.scale(frame, enemy_size)
            self.animations['walk'].append(scaled_frame)
            
            flash_frame = scaled_frame.copy()
            flash_frame.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.flash_animations['walk'].append(flash_frame)

    def animate(self):
        """Handles the enemy animation logic, including flash effect."""
        now = pygame.time.get_ticks()
        
        current_anim_set = self.flash_animations if self.is_flashing else self.animations

        animation_speed = 120
        if now - self.last_frame_update > animation_speed:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(current_anim_set[self.action])
            
            new_image = current_anim_set[self.action][self.frame_index]
            if self.direction == -1:
                new_image = pygame.transform.flip(new_image, True, False)
            
            center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect(center=center)

    def update(self):
        if self.is_flashing and pygame.time.get_ticks() - self.flash_timer > self.flash_duration:
            self.is_flashing = False

        self.animate()
        self.rect.x += self.speed * self.direction
        if abs(self.rect.centerx - self.start_x) > self.patrol_distance:
            self.direction *= -1

    def take_damage(self, amount):
        if self.is_flashing:
            return
        self.health -= amount
        if self.health <= 0:
            self.kill()
        else:
            self.is_flashing = True
            self.flash_timer = pygame.time.get_ticks()

class BossGate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 120)); self.image.fill(PURPLE)
        pygame.draw.rect(self.image, (138, 43, 226), (10, 10, 60, 100), 5)
        pygame.draw.rect(self.image, (75, 0, 130), (20, 20, 40, 80))
        self.rect = self.image.get_rect(center=(x, y))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__(); self.game = game
        
        if BOSS_IMAGE:
            self.original_image = pygame.image.load(BOSS_IMAGE).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (120, 120))
        else:
            self.original_image = pygame.Surface((120, 120)); self.original_image.fill(PURPLE)
        
        self.image = self.original_image.copy()
        self.flash_image = self.original_image.copy()
        self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 200; self.max_health = 200
        self.speed = 3; self.direction = 1
        self.shoot_delay = 1500
        self.last_shot = pygame.time.get_ticks()
        self.phase = 1; self.min_x = 100; self.max_x = 700

        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 150

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.is_flashing:
            if now - self.flash_timer > self.flash_duration:
                self.is_flashing = False
                self.image = self.original_image
        
        health_percentage = self.health / self.max_health
        if health_percentage < 0.5 and self.phase == 1: self.phase = 2; self.shoot_delay = 1000
        elif health_percentage < 0.25 and self.phase == 2: self.phase = 3; self.shoot_delay = 700
        
        self.rect.x += self.speed * self.direction
        if self.rect.left < self.min_x or self.rect.right > self.max_x: self.direction *= -1
        
        if now - self.last_shot > self.shoot_delay:
            self.shoot(); self.last_shot = now

    def shoot(self):
        if self.phase == 1:
            proj = BossProjectile(self.rect.centerx, self.rect.bottom, 0, 6)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)
        elif self.phase == 2:
            projectiles = [BossProjectile(self.rect.centerx, self.rect.bottom, angle*5, 6) for angle in [-0.3, 0, 0.3]]
            for proj in projectiles: self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)
        else: # Phase 3
            projectiles = [BossProjectile(self.rect.centerx, self.rect.bottom, angle*7, 7) for angle in [-0.5,-0.25,0,0.25,0.5]]
            for proj in projectiles: self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)

    def take_damage(self, amount):
        if self.is_flashing:
            return
        self.health -= amount
        if self.health <= 0: self.kill(); self.game.game_state = 'victory'
        else:
            self.is_flashing = True
            self.flash_timer = pygame.time.get_ticks()
            self.image = self.flash_image

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((15, 15)); pygame.draw.circle(self.image, RED, (7,7), 7)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy

    def update(self):
        self.rect.x += self.vx; self.rect.y += self.vy
        if not (-100<self.rect.top and self.rect.bottom<1000 and -100<self.rect.left and self.rect.right<2000):
            self.kill()
