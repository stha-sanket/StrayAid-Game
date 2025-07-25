# Street Paws Rescue - Python Game
import pygame
import random
import sys
import cairosvg
import io

# Game states
MENU = 0
COMMANDS = 1
GAME = 2
GAME_OVER = 3

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 215)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Paws Rescue")
clock = pygame.time.Clock()

# Game classes
class Animal:
    def __init__(self, x, y, animal_type, condition):
        self.x = x
        self.y = y
        self.type = animal_type
        self.condition = condition  # "hungry", "sick", "needs_shelter"
        self.rescued = False
        self.image = self.load_image()
        self.dx = random.choice([-1, 1]) * random.randint(2, 4) # Random speed
        self.dy = random.choice([-1, 1]) * random.randint(2, 4) # Random speed
        
    def load_image(self):
        # Load SVG and convert to Pygame surface
        svg_file = f"/home/ashuranoryoshi/Desktop/game/{self.type}.svg"
        
        # Render SVG to PNG in memory
        png_data = cairosvg.svg2png(url=svg_file, output_width=50, output_height=50)
        
        # Load PNG data into Pygame surface
        image_stream = io.BytesIO(png_data)
        surf = pygame.image.load(image_stream, svg_file)
        return surf
        
    def draw(self, surface):
        if not self.rescued:
            surface.blit(self.image, (self.x, self.y))
            # Draw condition indicator
            colors = {
                "sick": (255, 0, 0),     # Red
                "needs_shelter": (0, 255, 0), # Green
                "hungry": (255, 140, 0) # Orange
            }
            pygame.draw.circle(surface, colors[self.condition], (self.x + 25, self.y - 10), 5)
            
            # Display required tool
            tool_map = {
                "sick": "Medicine",
                "needs_shelter": "Blanket",
                "hungry": "Food"
            }
            font = pygame.font.SysFont(None, 20)
            tool_text = font.render(tool_map[self.condition], True, WHITE)
            surface.blit(tool_text, (self.x + 25 - tool_text.get_width() // 2, self.y - 30))

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off walls
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 50:
            self.dx *= -1
        if self.y <= 0 or self.y >= SCREEN_HEIGHT - 50:
            self.dy *= -1

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = 5
        # Load man.svg for the player character
        svg_file = "/home/ashuranoryoshi/Desktop/game/man.svg"
        png_data = cairosvg.svg2png(url=svg_file, output_width=40, output_height=60)
        image_stream = io.BytesIO(png_data)
        self.image = pygame.image.load(image_stream, svg_file)
        self.rescue_tools = ["food", "medicine", "blanket"]
        self.selected_tool = 0
        self.rescued_animals = []
        self.score = 0
        
    def move(self, dx, dy):
        self.x = max(0, min(SCREEN_WIDTH - 40, self.x + dx * self.speed))
        self.y = max(0, min(SCREEN_HEIGHT - 60, self.y + dy * self.speed))
        
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        # Draw current tool
        font = pygame.font.SysFont(None, 24)
        tool_text = font.render(f"Tool: {self.rescue_tools[self.selected_tool]}", True, WHITE)
        surface.blit(tool_text, (10, 10))
        
    def next_tool(self):
        self.selected_tool = (self.selected_tool + 1) % len(self.rescue_tools)
        print(f"Selected tool: {self.rescue_tools[self.selected_tool]}")
        # Play tool switch sound
        # pygame.mixer.Sound("tool_switch_sound.wav").play()
        
    def try_rescue(self, animal):
        # Simple rescue logic - in full game would be more complex
        if not animal.rescued:
            if (abs(self.x - animal.x) < 50 and abs(self.y - animal.y) < 50):
                # Check if correct tool is being used
                if (animal.condition == "hungry" and self.rescue_tools[self.selected_tool] == "food") or \
                   (animal.condition == "sick" and self.rescue_tools[self.selected_tool] == "medicine") or \
                   (animal.condition == "needs_shelter" and self.rescue_tools[self.selected_tool] == "blanket"):
                    animal.rescued = True
                    self.rescued_animals.append(animal)
                    self.score += 100 # Add points for rescue
                    # Play rescue sound
                    # pygame.mixer.Sound("rescue_sound.wav").play()
                    return True
        return False

# Game setup
def setup_game():
    player = Player()
    animals = []
    
    # Create random animals
    animal_types = ["dog", "cat", "bird"]
    conditions = ["hungry", "sick", "needs_shelter"]
    
    for _ in range(5):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        animal_type = random.choice(animal_types)
        condition = random.choice(conditions)
        animals.append(Animal(x, y, animal_type, condition))
    
    return player, animals

# Main game loop
# Helper function to draw text
def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

# Helper function to draw a button
def draw_button(surface, rect, color, text, text_color, font_size):
    pygame.draw.rect(surface, color, rect)
    draw_text(surface, text, font_size, text_color, rect.centerx, rect.centery)
    return rect

def main():
    current_game_state = MENU
    player, animals = setup_game()
    print(f"Player object after initial setup_game(): {player}")
    game_timer = 60 * FPS # Initial game timer
    running = True
    
    while running:
        # Draw background
        screen.fill((80, 200, 80)) # Lighter green for grass
        pygame.draw.rect(screen, (60, 180, 60), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)) # Darker green for foreground grass
        pygame.draw.rect(screen, (139, 69, 19), (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80)) # Brown path
        pygame.draw.rect(screen, (160, 82, 45), (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 60)) # Lighter brown path

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):
                        current_game_state = GAME
                    elif commands_button_rect.collidepoint(event.pos):
                        current_game_state = COMMANDS
            elif current_game_state == COMMANDS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button_rect.collidepoint(event.pos):
                        current_game_state = MENU
            elif current_game_state == GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for animal in animals:
                            if player.try_rescue(animal):
                                print(f"Rescued a {animal.type}!")
                    elif event.key == pygame.K_TAB:
                        player.next_tool()

        

        if current_game_state == MENU:
            draw_text(screen, "Street Paws Rescue", 74, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            start_button_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50), BLUE, "Start Game", WHITE, 36)
            commands_button_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50), BLUE, "Commands", WHITE, 36)
        elif current_game_state == COMMANDS:
            draw_text(screen, "Commands", 64, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, "Movement: Arrow Keys or WASD", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
            draw_text(screen, "Switch Tools: TAB", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90)
            draw_text(screen, "Rescue: SPACEBAR (with correct tool)", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
            draw_text(screen, "Animal Conditions:", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
            draw_text(screen, "  Orange: Hungry", 26, (255, 140, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
            draw_text(screen, "  Red: Sick", 26, (255, 0, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            draw_text(screen, "  Green: Needs Shelter", 26, (0, 255, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            draw_text(screen, "Tool Usage:", 30, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)
            draw_text(screen, "  Food: Hungry", 26, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)
            draw_text(screen, "  Medicine: Sick", 26, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140)
            draw_text(screen, "  Blanket: Needs Shelter", 26, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160)
            back_button_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50), BLUE, "Back to Menu", WHITE, 36)
        elif current_game_state == GAME:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
                
            player.move(dx, dy)
            
            # Move and draw animals
            for animal in animals:
                if not animal.rescued:
                    animal.move()
                animal.draw(screen)
                
            player.draw(screen)
            
            # Draw score and timer
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH - 200, 10))
            
            timer_seconds = game_timer // FPS
            timer_text = font.render(f"Time: {timer_seconds}", True, WHITE)
            screen.blit(timer_text, (SCREEN_WIDTH - 200, 50))

            # Update game timer
            game_timer -= 1
            if game_timer <= 0:
                current_game_state = GAME_OVER

            if len(player.rescued_animals) == len(animals):
                win_font = pygame.font.SysFont(None, 100)
                win_text = win_font.render("You Win!", True, (0, 255, 0))
                text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(win_text, text_rect)
                pygame.display.flip()
                pygame.time.wait(3000)
                current_game_state = GAME_OVER
        
        pygame.display.flip()
        clock.tick(FPS)

        if current_game_state == GAME_OVER:
            draw_text(screen, "Game Over!", 74, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, f"Final Score: {player.score}", 50, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            restart_button_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50), BLUE, "Restart", WHITE, 36)
            menu_button_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 50), BLUE, "Main Menu", WHITE, 36)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    player, animals = setup_game()
                    game_timer = 60 * FPS
                    current_game_state = GAME
                elif menu_button_rect.collidepoint(event.pos):
                    current_game_state = MENU
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()