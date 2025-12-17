import pygame
import random
import math
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GOLD, BLUE, PURPLE, RED, GREEN, YELLOW, GRAY
from inventory import TIER_COLORS

class ConfettiParticle:
    def __init__(self, x, y, color, vx, vy, rotation_speed):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.alpha = 255
        self.size = random.randint(5, 10)
        self.rotation = 0
        self.rotation_speed = rotation_speed
        self.lifetime = random.randint(30, 90) # frames

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5 # gravity
        self.alpha -= 3
        if self.alpha < 0: self.alpha = 0
        self.size -= 0.1
        if self.size < 0: self.size = 0
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.lifetime -= 1

    def draw(self, screen):
        if self.alpha <= 0 or self.size <= 0 or self.lifetime <= 0: return

        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, self.alpha)) # Fill with color and alpha

        rotated_s = pygame.transform.rotate(s, self.rotation)
        rect = rotated_s.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_s, rect)

class RibbonParticle:
    def __init__(self, x, y, color, vx, vy, rotation_speed):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.alpha = 255
        self.width = random.randint(3, 7)
        self.height = random.randint(15, 30)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = rotation_speed
        self.lifetime = random.randint(40, 100) # frames

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5 # gravity
        self.alpha -= 2
        if self.alpha < 0: self.alpha = 0
        self.width -= 0.05
        self.height -= 0.1
        if self.width < 0: self.width = 0
        if self.height < 0: self.height = 0
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.lifetime -= 1

    def draw(self, screen):
        if self.alpha <= 0 or self.width <= 0 or self.height <= 0 or self.lifetime <= 0: return

        s = pygame.Surface((max(1, int(self.width)), max(1, int(self.height))), pygame.SRCALPHA)
        s.fill((*self.color, self.alpha)) # Fill with color and alpha

        rotated_s = pygame.transform.rotate(s, self.rotation)
        rect = rotated_s.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_s, rect)

def play_gacha_animation(screen, revealed_item_info, gun_images, font):
    """
    Plays a gacha reveal animation, blocking until complete.
    - Plays a synchronized sound.
    - Shows a suspenseful shaking capsule for 2.55 seconds.
    - Reveals the item with a flash and scaling effect.
    - Returns the revealed item info.
    """
    # Load and play the synchronized audio
    try:
        gacha_sound = pygame.mixer.Sound(os.path.join('assets', 'audio', 'drumrolltada.mp3'))
        gacha_channel = pygame.mixer.find_channel(True)
        gacha_channel.play(gacha_sound)
    except pygame.error as e:
        print(f"Could not load or play gacha sound: {e}")
        # Even if sound fails, proceed with animation
        gacha_sound = None

    # Load gachabox.png
    try:
        selected_case_image = pygame.image.load(os.path.join('assets', 'gachabox.png')).convert_alpha()
        frame_width = selected_case_image.get_width()
        frame_height = selected_case_image.get_height()
    except pygame.error as e:
        print(f"Could not load or process gachabox.png: {e}. Using a placeholder square.")
        frame_width = 80
        frame_height = 80
        selected_case_image = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        selected_case_image.fill(GRAY) # Fallback to a gray square

    # Gacha capsule position (centered, will use for drawing case image)
    crate_pos_x = (SCREEN_WIDTH / 2) - (frame_width / 2)
    crate_pos_y = (SCREEN_HEIGHT / 2) - (frame_height / 2)
    
    # Animation timing
    start_time = pygame.time.get_ticks()
    animation_duration = 5000  # 5 seconds total
    reveal_time = 2550  # 2.55 seconds

    # Revealed item details
    gun_id = revealed_item_info['gun_id']
    item_image = gun_images.get(gun_id)
    if item_image is None: # Fallback if image is missing
        item_image = pygame.Surface((150, 150), pygame.SRCALPHA)
        item_image.fill(PURPLE)

    tier = revealed_item_info['tier']
    tier_color = TIER_COLORS.get(tier, WHITE)
    gun_name = revealed_item_info.get('name', 'Unknown Gun')

    confetti_particles = []
    ribbon_particles = [] # New list for ribbon particles
    confetti_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, GOLD]

    clock = pygame.time.Clock()
    animating = True
    while animating:
        elapsed_time = pygame.time.get_ticks() - start_time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                animating = False # Allow skipping

        # --- Update ---
        # Update confetti
        for particle in list(confetti_particles): # Iterate over a copy
            particle.update()
            if particle.alpha <= 0 or particle.size <= 0 or particle.lifetime <= 0:
                confetti_particles.remove(particle)
        
        # Update ribbons
        for particle in list(ribbon_particles): # Iterate over a copy
            particle.update()
            if particle.alpha <= 0 or particle.width <= 0 or particle.height <= 0 or particle.lifetime <= 0:
                ribbon_particles.remove(particle)

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw confetti (before anything else, so it's behind the item/text)
        for particle in confetti_particles:
            particle.draw(screen)
        
        # Draw ribbons
        for particle in ribbon_particles:
            particle.draw(screen)


        if elapsed_time < reveal_time:
            # --- Suspense Phase ---
            # Shaking effect for the crate position
            shake_x = random.randint(-5, 5) if elapsed_time % 100 < 50 else 0 # Shake every other 50ms
            shake_y = random.randint(-5, 5) if elapsed_time % 100 < 50 else 0

            # Draw current crate frame (static, randomly selected case)
            case_rect = selected_case_image.get_rect(center=(SCREEN_WIDTH / 2 + shake_x, SCREEN_HEIGHT / 2 + shake_y)) # Use center for blitting
            screen.blit(selected_case_image, case_rect)
            
            text_surf = font.render("Opening...", True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150))
            screen.blit(text_surf, text_rect)

        else:
            # --- Reveal Phase ---
            if not confetti_particles and not ribbon_particles: # Generate confetti & ribbons only once
                # Generate confetti burst at the center of the screen
                for _ in range(200): # 200 particles for a crazy effect
                    confetti_particles.append(ConfettiParticle(
                        SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        random.choice(confetti_colors),
                        random.uniform(-7, 7), random.uniform(-12, -4), # vx, vy (upwards initial velocity, increased a bit)
                        random.uniform(-15, 15) # rotation_speed
                    ))
                
                # Generate ribbon burst at the center of the screen
                for _ in range(50): # 50 ribbons
                    ribbon_particles.append(RibbonParticle(
                        SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        random.choice(confetti_colors),
                        random.uniform(-6, 6), random.uniform(-10, -3), # vx, vy
                        random.uniform(-10, 10) # rotation_speed
                    ))

            # 1. Flash effect
            reveal_progress = (elapsed_time - reveal_time) / 500  # Flash lasts 0.5s
            if reveal_progress < 1.0:
                flash_alpha = 255 * (1 - reveal_progress)
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, flash_alpha))
                screen.blit(flash_surface, (0, 0))

            # 2. Scale up the item
            scale_progress = min(1.0, (elapsed_time - reveal_time) / 1000) # Scale over 1s
            # Ease-out-back easing function for a nice bounce effect
            c1 = 1.70158
            c3 = c1 + 1
            ease_scale = 1 + c3 * pow(scale_progress - 1, 3) + c1 * pow(scale_progress - 1, 2)

            scaled_width = int(item_image.get_width() * ease_scale)
            scaled_height = int(item_image.get_height() * ease_scale)

            if scaled_width > 0 and scaled_height > 0:
                display_image = pygame.transform.scale(item_image, (scaled_width, scaled_height))
                image_rect = display_image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
                
                # Draw glowing border behind image
                border_size = 10
                glow_rect = image_rect.inflate(border_size * 2, border_size * 2)
                pygame.draw.rect(screen, tier_color, glow_rect, border_size, border_radius=20)
                
                screen.blit(display_image, image_rect)


            # 3. Display item text (fade in)
            text_fade_progress = min(1.0, (elapsed_time - reveal_time - 500) / 500) # Fade in after 0.5s
            if text_fade_progress > 0:
                # Name
                name_surf = font.render(gun_name, True, tier_color)
                name_surf.set_alpha(255 * text_fade_progress)
                name_rect = name_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
                screen.blit(name_surf, name_rect)
                
                # Tier
                tier_surf = font.render(f"({tier})", True, tier_color)
                tier_surf.set_alpha(255 * text_fade_progress)
                tier_rect = tier_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150))
                screen.blit(tier_surf, tier_rect)

                # Duplicate status
                if revealed_item_info['is_duplicate']:
                    dup_surf = font.render("Duplicate!", True, RED)
                    dup_surf.set_alpha(255 * text_fade_progress)
                    dup_rect = dup_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 210))
                    screen.blit(dup_surf, dup_rect)

        if elapsed_time > animation_duration:
            animating = False

        pygame.display.flip()
        clock.tick(60)

    if gacha_sound and gacha_channel:
        gacha_channel.stop()

    return revealed_item_info