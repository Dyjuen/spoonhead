import pygame
import psutil
import os

class Benchmark:
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.width = 300
        self.height = 150
        self.x = screen_width - self.width - 10
        self.y = 10
        
        # Data storage (Max 300 frames of history)
        self.history_limit = 300
        self.fps_history = []
        self.cpu_history = []
        self.ram_history = []
        
        self.font = pygame.font.SysFont("Arial", 12)
        self.process = psutil.Process(os.getpid())
        
        # Timers
        self.last_update = 0
        self.update_interval = 100 # Update data every 100ms

    def toggle(self):
        self.active = not self.active

    def update(self, clock):
        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.update_interval:
            # 1. Get FPS
            fps = clock.get_fps()
            self.fps_history.append(fps)
            
            # 2. Get CPU Usage (System wide or Process specific)
            # interval=None is non-blocking
            cpu = psutil.cpu_percent(interval=None) 
            self.cpu_history.append(cpu)
            
            # 3. Get RAM Usage (in MB)
            ram_bytes = self.process.memory_info().rss
            ram_mb = ram_bytes / (1024 * 1024)
            self.ram_history.append(ram_mb)
            
            # Trim lists
            if len(self.fps_history) > self.history_limit: self.fps_history.pop(0)
            if len(self.cpu_history) > self.history_limit: self.cpu_history.pop(0)
            if len(self.ram_history) > self.history_limit: self.ram_history.pop(0)
            
            self.last_update = current_time

    def draw_graph(self, surface, data, color, y_offset, max_val, label):
        if not data: return
        
        # Background for single graph strip
        graph_h = 40
        pygame.draw.rect(surface, (0, 0, 0, 150), (self.x, self.y + y_offset, self.width, graph_h))
        
        # Draw Lines
        if len(data) > 1:
            points = []
            for i, val in enumerate(data):
                # Normalize x to width
                px = self.x + (i / self.history_limit) * self.width
                # Normalize y to height (inverted because y goes down)
                # Clamp val to max_val to prevent drawing out of box
                normalized_val = min(val, max_val) / max_val
                py = (self.y + y_offset + graph_h) - (normalized_val * graph_h)
                points.append((px, py))
            
            pygame.draw.lines(surface, color, False, points, 1)

        # Draw Text Value
        current_val = data[-1]
        text_surf = self.font.render(f"{label}: {current_val:.1f}", True, color)
        surface.blit(text_surf, (self.x + 5, self.y + y_offset + 5))

    def draw(self, screen):
        if not self.active:
            return

        # Draw FPS (Green) - Scale 0 to 144
        self.draw_graph(screen, self.fps_history, (0, 255, 0), 0, 144, "FPS")
        
        # Draw CPU (Red) - Scale 0 to 100%
        self.draw_graph(screen, self.cpu_history, (255, 50, 50), 45, 100, "CPU %")
        
        # Draw RAM (Blue) - Scale 0 to 500 MB (Adjust as needed)
        self.draw_graph(screen, self.ram_history, (50, 150, 255), 90, 500, "RAM (MB)")
