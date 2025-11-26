import pygame
import random
import os
import math
import time
from settings import *

class SpriteSheet:
    """Utility for loading and parsing sprite sheets."""
    def __init__(self, filename):
        try:
            self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load sprite sheet: {filename}")
            raise e

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_animation_frames(self, frame_width, frame_height):
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        for x in range(0, sheet_width, frame_width):
            frame = self.get_image(x, 0, frame_width, self.sprite_sheet.get_height())
            frames.append(frame)
        return frames

class Player(pygame.sprite.Sprite):
    """Player character with a reliable counter-based double jump."""
    def __init__(self, x, y, upgrades=None):
        super().__init__()
        
        self.upgrades = upgrades if upgrades else {}
        self.load_animations()
        self.action = 'idle'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.max_health = 100
        self.coins = 0
        
        self.vx = 0
        self.vy = 0
        self.speed = 6
        self.jump_power = -16
        self.gravity = 0.8
        
        # Counter-based double jump
        self.on_ground = False
        self.jumps_made = 0
        
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 200
        self.dash_speed = 15
        self.dash_cooldown = 500
        self.last_dash = 0
        
        self.can_shoot = True
        self.shoot_cooldown = 250
        self.last_shot = 0
        self.facing_right = True

        self.apply_upgrades()
        self.health = self.max_health

    def apply_upgrades(self):
        self.health_upgrade = self.upgrades.get('health_up', False)
        self.spread_shot = self.upgrades.get('spread_shot', False)
        self.burst_shot = self.upgrades.get('burst_shot', False)

        if self.health_upgrade:
            self.max_health += 25

        

    def load_animations(self):
        self.animations = {'idle': [], 'run': [], 'jump': [], 'double_jump': []}
        player_size = (60, 60)
        for anim_type, sprite_path in [
            ('idle', PLAYER_IDLE_SPRITE), ('run', PLAYER_RUN_SPRITE),
            ('jump', PLAYER_JUMP_SPRITE), ('double_jump', PLAYER_DOUBLE_JUMP_SPRITE)
        ]:
            try:
                sheet = SpriteSheet(sprite_path)
                frames = sheet.get_animation_frames(48, 48)
                scaled_frames = [pygame.transform.scale(frame, player_size) for frame in frames]
                self.animations[anim_type] = scaled_frames
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load player animation: {sprite_path}")
                placeholder_frame = pygame.Surface(player_size, pygame.SRCALPHA); placeholder_frame.fill(BLUE)
                self.animations[anim_type] = [placeholder_frame] * 4

    def animate(self):
        now = pygame.time.get_ticks()
        if self.action == 'double_jump' and self.frame_index >= len(self.animations['double_jump']) - 1:
            self.set_action('jump')
        if now - self.last_frame_update > 100:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations.get(self.action, [self.image]))
            new_image = self.animations[self.action][self.frame_index]
            if not self.facing_right:
                new_image = pygame.transform.flip(new_image, True, False)
            center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect(center=center)

    def set_action(self, new_action):
        if self.action != new_action:
            self.action = new_action
            self.frame_index = 0

    def update(self, move_input, platforms):
        if not self.on_ground:
            if self.vy > 0 and self.action != 'double_jump': self.set_action('jump') # Falling
        elif move_input is not None and (move_input < 0.4 or move_input > 0.6): self.set_action('run')
        else: self.set_action('idle')

        self.vx = 0
        if move_input is not None:
            if self.dashing:
                if pygame.time.get_ticks() - self.dash_timer > self.dash_duration: self.dashing = False
                self.vx = self.dash_speed * (1 if self.facing_right else -1)
            else:
                if move_input < 0.4: self.vx = -self.speed; self.facing_right = False
                elif move_input > 0.6: self.vx = self.speed; self.facing_right = True
        
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
                self.jumps_made = 0 # Reset jump counter on landing
                if isinstance(platform, MovingPlatform): self.rect.x += platform.speed * platform.direction
            elif self.vy < 0:
                self.rect.top = platform.rect.bottom
                self.vy = 0
        
        self.animate()

    def jump(self):
        if self.jumps_made < 2:
            self.vy = self.jump_power
            self.on_ground = False
            self.set_action('double_jump' if self.jumps_made == 1 else 'jump')
            self.jumps_made += 1

    def dash(self):
        current_time = pygame.time.get_ticks()
        if not self.dashing and current_time - self.last_dash > self.dash_cooldown:
            self.dashing = True; self.dash_timer = current_time; self.last_dash = current_time

    def shoot(self, shoot_direction='horizontal'):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.last_shot = current_time
            projectiles = pygame.sprite.Group()
            
            direction = 1 if self.facing_right else -1
            
            if self.burst_shot:
                for i in range(3):
                    # Slight delay for burst would be complex, so we spawn them together
                    # with a slight offset to simulate a burst.
                    proj = Projectile(self.rect.centerx + (i * 15 * direction), self.rect.centery, 12 * direction, 0)
                    projectiles.add(proj)
                return projectiles

            if self.spread_shot:
                angles = [-15, 0, 15] # Degrees
                for angle in angles:
                    rad_angle = math.radians(angle)
                    vx = 12 * direction * math.cos(rad_angle)
                    vy = 12 * math.sin(rad_angle)
                    projectiles.add(Projectile(self.rect.centerx, self.rect.centery, vx, vy))
                return projectiles

            # Default shot
            speed = 12
            sqrt2_half = 0.7071 # Approximation of sin(45) and cos(45)

            if shoot_direction == 'up':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, 0, -speed))
            elif shoot_direction == 'down':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, 0, speed))
            elif shoot_direction == 'up_right':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * sqrt2_half, -speed * sqrt2_half))
            elif shoot_direction == 'up_left':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed * sqrt2_half, -speed * sqrt2_half))
            elif shoot_direction == 'down_right':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * sqrt2_half, speed * sqrt2_half))
            elif shoot_direction == 'down_left':
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed * sqrt2_half, speed * sqrt2_half))
            elif shoot_direction == 'left':
                 projectiles.add(Projectile(self.rect.centerx, self.rect.centery, -speed, 0))
            elif shoot_direction == 'right':
                 projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed, 0))
            else: # horizontal
                projectiles.add(Projectile(self.rect.centerx, self.rect.centery, speed * direction, 0))
            
            
            return projectiles
        return None

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0: self.health = 0

class Enemy(pygame.sprite.Sprite):
    """Enemy that patrols and shoots, with NO flashing effect."""
    def __init__(self, x, y, patrol_distance=100, speed=2, shoot_cooldown=2.0):
        super().__init__()
        self.load_animations()
        self.action = 'walk'
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.health, self.speed, self.direction = 30, speed, 1
        self.start_x, self.patrol_distance = x, patrol_distance
        self.shoot_cooldown, self.last_shot_time = shoot_cooldown, time.time()
        self.detection_range = 400

    def load_animations(self):
        self.animations = {'walk': []}
        enemy_size = (64, 64)
        try:
            sheet = SpriteSheet(ENEMY_WALK_SPRITE)
            frames = sheet.get_animation_frames(48, 48) 
            for frame in frames:
                self.animations['walk'].append(pygame.transform.scale(frame, enemy_size))
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load enemy animation: {ENEMY_WALK_SPRITE}")
            placeholder = pygame.Surface(enemy_size); placeholder.fill(RED)
            self.animations['walk'] = [placeholder]

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 120:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.action])
            new_image = self.animations[self.action][self.frame_index]
            if self.direction == -1: new_image = pygame.transform.flip(new_image, True, False)
            center = self.rect.center
            self.image, self.rect = new_image, new_image.get_rect(center=center)

    def update(self, player, all_sprites_group, enemy_projectiles_group):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.centerx - self.start_x) > self.patrol_distance: self.direction *= -1
        self.animate()
        if abs(player.rect.centerx - self.rect.centerx) < self.detection_range and time.time() - self.last_shot_time > self.shoot_cooldown:
            self.shoot_at_player(player, all_sprites_group, enemy_projectiles_group)
            self.last_shot_time = time.time()

    def shoot_at_player(self, player, all_sprites, projectiles_group):
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0: return
        vx, vy = (dx / distance) * 6, (dy / distance) * 6
        proj = EnemyProjectile(self.rect.centerx, self.rect.centery, vx, vy)
        all_sprites.add(proj); projectiles_group.add(proj)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0: self.kill()

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA); self.image.fill(ORANGE)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy, self.lifetime = vx, vy, 180

    def update(self):
        self.rect.move_ip(self.vx, self.vy); self.lifetime -= 1
        if self.lifetime <= 0 or not self.rect.colliderect(pygame.Rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)): self.kill()

class Projectile(pygame.sprite.Sprite):
    animation_frames_right, animation_frames_left = [], []
    @staticmethod
    def load_images():
        if Projectile.animation_frames_right: return
        bullet_size, sprite_paths = (20, 10), [os.path.join("assets", "Bullets", f"7_{i}.png") for i in "12"]
        try:
            for path in sprite_paths:
                img = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(img, bullet_size)
                Projectile.animation_frames_right.append(scaled)
                Projectile.animation_frames_left.append(pygame.transform.flip(scaled, True, False))
        except pygame.error:
            print("Warning: Player projectile images not found."); surf = pygame.Surface(bullet_size, pygame.SRCALPHA); surf.fill(YELLOW)
            Projectile.animation_frames_right = [surf]*2; Projectile.animation_frames_left = [surf]*2

    def __init__(self, x, y, vx, vy):
        super().__init__()
        direction = 1 if vx >= 0 else -1
        self.anim_frames = Projectile.animation_frames_right if direction == 1 else Projectile.animation_frames_left
        self.frame_index, self.last_frame_update = 0, pygame.time.get_ticks()
        self.image = self.anim_frames[self.frame_index]; self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy

    def update(self):
        if pygame.time.get_ticks() - self.last_frame_update > 100:
            self.last_frame_update = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.anim_frames); self.image = self.anim_frames[self.frame_index]
        self.rect.move_ip(self.vx, self.vy)
        if not self.rect.colliderect(pygame.Rect(-100,-100,SCREEN_WIDTH+200,SCREEN_HEIGHT+200)): self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height)); self.image.fill(BROWN)
        pygame.draw.rect(self.image, DARK_BROWN, (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_axis='x', move_range=100, speed=2):
        super().__init__(x, y, width, height)
        self.start_pos = pygame.math.Vector2(x, y)
        self.move_axis, self.move_range, self.speed, self.direction = move_axis, move_range, speed, 1

    def update(self):
        if self.move_axis == 'x': self.rect.x += self.speed * self.direction
        else: self.rect.y += self.speed * self.direction
        if abs((self.rect.x if self.move_axis == 'x' else self.rect.y) - (self.start_pos.x if self.move_axis == 'x' else self.start_pos.y)) >= self.move_range:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10); pygame.draw.circle(self.image, YELLOW, (10, 10), 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset, self.bob_range, self.original_y = random.uniform(0, 2*math.pi), 4, y

    def update(self):
        self.rect.y = self.original_y + int(math.sin(self.bob_offset) * self.bob_range); self.bob_offset += 0.1

class BossGate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(); self.image = pygame.Surface((80, 120), pygame.SRCALPHA); self.image.fill(PURPLE)
        pygame.draw.rect(self.image, GOLD, self.image.get_rect(), 5); font = pygame.font.Font(None, 30)
        self.image.blit(font.render("BOSS", True, WHITE), (15, 45)); self.rect = self.image.get_rect(center=(x, y))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, game, health=500, speed=3, shoot_interval=60, phases=3, boss_type=1):
        super().__init__(); self.game = game
        self.max_health, self.health, self.phase, self.max_phases = health, health, 1, phases
        self.boss_type = boss_type
        try:
            self.original_image = pygame.transform.scale(pygame.image.load(BOSS_IMAGE).convert_alpha(), (120, 120))
        except (pygame.error, TypeError):
            self.original_image = pygame.Surface((120, 120), pygame.SRCALPHA); self.original_image.fill(PURPLE)
            pygame.draw.circle(self.original_image, DARK_PURPLE, (60, 60), 50)
        self.image, self.flash_image = self.original_image.copy(), self.original_image.copy()
        self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        self.rect = self.image.get_rect(center=(x, y)); self.vx, self.vy = speed, speed * 0.66
        self.shoot_timer, self.base_shoot_interval = 0, shoot_interval; self.shoot_interval = shoot_interval
        self.pattern_counter, self.is_flashing, self.flash_timer, self.flash_duration = 0, False, 0, 150

    def update(self):
        if self.health <= 0: return
        if self.max_phases>1 and self.health<self.max_health*0.66 and self.phase==1: self.phase,self.shoot_interval=2,self.base_shoot_interval*0.75
        elif self.max_phases>2 and self.health<self.max_health*0.33 and self.phase==2: self.phase,self.shoot_interval=3,self.base_shoot_interval*0.5
        self.rect.x+=self.vx; self.rect.y+=self.vy
        if self.rect.left<=0 or self.rect.right>=SCREEN_WIDTH: self.vx *= -1
        if self.rect.top<=100 or self.rect.bottom>=400: self.vy *= -1
        self.shoot_timer+=1
        if self.shoot_timer>=self.shoot_interval: self.shoot(); self.shoot_timer=0
        if self.is_flashing and pygame.time.get_ticks()-self.flash_timer>self.flash_duration: self.is_flashing=False; self.image=self.original_image

    def shoot(self):
        if self.boss_type == 1:
            self.shoot_pattern_boss1()
        elif self.boss_type == 2:
            self.shoot_pattern_boss2()
        elif self.boss_type == 3:
            self.shoot_pattern_boss3()
        else: # Default behavior
            self.shoot_pattern_1()

    def shoot_pattern_boss1(self):
        # Boss 1 only has one simple pattern.
        self.shoot_pattern_1()

    def shoot_pattern_boss2(self):
        # Boss 2 uses pattern 2 in phase 1, and pattern 3 in phase 2.
        if self.phase == 1:
            self.shoot_pattern_2()
        else:
            self.shoot_pattern_3()

    def shoot_pattern_boss3(self):
        # Boss 3 cycles through all patterns based on its phase.
        if self.phase == 1:
            self.shoot_pattern_1()
        elif self.phase == 2:
            self.shoot_pattern_2()
        else:
            self.shoot_pattern_3()

    def shoot_pattern_1(self):
        proj = BossProjectile(self.rect.centerx, self.rect.bottom, 0, 5)
        self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)

    def shoot_pattern_2(self):
        for angle in range(0, 360, 45):
            proj = BossProjectile(self.rect.centerx, self.rect.centery, math.cos(math.radians(angle))*4, math.sin(math.radians(angle))*4)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)

    def shoot_pattern_3(self):
        for i in range(2):
            angle = (self.pattern_counter*15 + i*180)%360
            proj = BossProjectile(self.rect.centerx, self.rect.centery, math.cos(math.radians(angle))*5, math.sin(math.radians(angle))*5)
            self.game.all_sprites.add(proj); self.game.boss_projectiles.add(proj)
        self.pattern_counter+=1

    def take_damage(self, amount):
        if self.is_flashing: return
        self.health -= amount
        if self.health <= 0: self.kill(); return
        self.is_flashing=True; self.flash_timer=pygame.time.get_ticks(); self.image=self.flash_image

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy):
        super().__init__(); self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PINK, (8, 8), 8); pygame.draw.circle(self.image, PURPLE, (8, 8), 5)
        self.rect = self.image.get_rect(center=(x, y)); self.vx, self.vy = vx, vy

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        if not self.rect.colliderect(pygame.Rect(-50,-50,SCREEN_WIDTH+100,SCREEN_HEIGHT+100)): self.kill()