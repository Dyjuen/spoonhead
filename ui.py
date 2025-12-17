import pygame
from settings import PIXEL_FONT

class Button:
    """Simple button class"""
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=pygame.Color('white'), font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(PIXEL_FONT, font_size)

    def draw(self, screen, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.text_color, self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f"DEBUG BUTTON: Click detected on '{self.text}'")
            print(f"DEBUG BUTTON: Button Rect: {self.rect}")
            print(f"DEBUG BUTTON: Mouse Position: {mouse_pos}")
            if self.rect.collidepoint(mouse_pos):
                print(f"DEBUG BUTTON: Collision detected for '{self.text}'!")
                return True
            else:
                print(f"DEBUG BUTTON: NO collision for '{self.text}'. Mouse not on button.")
        return False
