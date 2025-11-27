"""
Demo script untuk menunjukkan cara menggunakan sistem 2 controller
dengan fitur "press button to join"
"""

import pygame
from controller import ControllerManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("2 Controller Demo - Press Button to Join")
    clock = pygame.time.Clock()
    
    # Initialize controller manager (max 2 players)
    controller_manager = ControllerManager(max_players=2)
    
    # Player positions (untuk demo visual)
    player_positions = [
        [100, 300],  # Player 1
        [700, 300]   # Player 2
    ]
    player_colors = [
        (0, 255, 0),    # Green for Player 1
        (255, 100, 100) # Red for Player 2
    ]
    
    running = True
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        # Update controller manager (check for join inputs)
        controller_manager.update()
        
        # Get actions from all active controllers
        all_actions = controller_manager.get_all_actions()
        
        # Process actions for each player
        for actions in all_actions:
            player_id = actions['player_id']
            
            # Movement (convert from 0.0-1.0 to -1 to 1)
            move_x = (actions['move_x'] - 0.5) * 2.0
            player_positions[player_id][0] += move_x * 5
            
            # Jump (move up when pressed)
            if actions['jump']:
                player_positions[player_id][1] -= 3
            else:
                # Simple gravity
                if player_positions[player_id][1] < 300:
                    player_positions[player_id][1] += 2
            
            # Keep in bounds
            player_positions[player_id][0] = max(50, min(750, player_positions[player_id][0]))
            player_positions[player_id][1] = max(50, min(550, player_positions[player_id][1]))
        
        # Draw
        screen.fill((30, 30, 50))
        
        # Draw title
        title = font.render("2 Controller Demo", True, (255, 255, 255))
        screen.blit(title, (250, 30))
        
        # Draw active players
        active_controllers = controller_manager.get_active_controllers()
        for i, pos in enumerate(player_positions):
            if i < len(active_controllers):
                # Draw player circle
                pygame.draw.circle(screen, player_colors[i], 
                                 (int(pos[0]), int(pos[1])), 30)
                # Draw player label
                label = small_font.render(f"P{i+1}", True, (255, 255, 255))
                screen.blit(label, (int(pos[0]) - 15, int(pos[1]) - 10))
        
        # Draw controller status
        status_texts = controller_manager.get_status_texts()
        y_offset = 100
        for i, text in enumerate(status_texts):
            color = player_colors[i] if i < len(player_colors) else (255, 255, 255)
            status = small_font.render(text, True, color)
            screen.blit(status, (50, y_offset))
            y_offset += 30
        
        # Draw instructions
        instructions = [
            "Player 1: Always active (Controller 1 or Keyboard)",
            "Player 2: Press any button on Controller 2 to join",
            "",
            "Controls: Left Stick = Move, A = Jump",
            "Keyboard (P1): WASD/Arrows = Move, Space = Jump"
        ]
        y_offset = 400
        for instruction in instructions:
            inst_text = small_font.render(instruction, True, (180, 180, 180))
            screen.blit(inst_text, (50, y_offset))
            y_offset += 25
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
