import pygame

class Parallax:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.layers = []
        for i in range(6):
            image = pygame.image.load(f'assets/Background/{i}.png').convert_alpha()
            scaled_image = self.scale_image(image)
            
            speed = 0
            if i == 5:
                speed = 0
            elif i == 4:
                speed = 0.05
            else:
                speed = (5 - i) * 0.1

            self.layers.append({
                'image': scaled_image,
                'speed': speed,
                'x': 0
            })
        
        
        self.layers.reverse()

    def scale_image(self, image):
        image_height = image.get_height()
        scale = self.screen_height / image_height
        new_width = image.get_width() * scale
        return pygame.transform.scale(image, (int(new_width), self.screen_height))

    def update(self, camera_x):
        for layer in self.layers:
            layer['x'] = -camera_x * layer['speed']

    def draw(self, screen):
        for layer in self.layers:
            image = layer['image']
            image_width = image.get_width()
            x = layer['x'] % image_width

            screen.blit(image, (x, 0))

            if x > 0:
                screen.blit(image, (x - image_width, 0))

            if x < self.screen_width:
                 screen.blit(image, (x + image_width, 0))
