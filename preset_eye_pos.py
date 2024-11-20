import pygame
import time
import math

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

eyes = pygame.Rect(217,240,140,140) # (x,y,width,height)
pupil = pygame.Rect(217,240,40,40)

""" 
list of all the positions within the eye
(eyes.x + 0, eyes.y + 0),     # Center
(eyes.x + 50, eyes.y + 50),   # Bottom right
(eyes.x + 50, eyes.y -50),    # Top right
(eyes.x + 75, eyes.y + 0),    # Center right
(eyes.x + 0, eyes.y - 75),    # Center top
(eyes.x - 50, eyes.y + 50),   # Bottom left
(eyes.x - 75, eyes.y + 0),    # Center left
(eyes.x - 50, eyes.y - 50),   # Top left
(eyes.x + 0, eyes.y + 75),    # Center bottom
"""

# Define predefined positions within the eye
pupil_positions = {
    pygame.K_1: (eyes.x + 50, eyes.y + 50),   # Bottom right
    pygame.K_2: (eyes.x + 50, eyes.y + 50),   # Bottom right
    pygame.K_3: (eyes.x - 75, eyes.y + 0),    # Center left
    pygame.K_4: (eyes.x + 75, eyes.y + 0),    # Center right
    pygame.K_5: (eyes.x + 0, eyes.y - 75),    # Center top
    pygame.K_6: (eyes.x - 50, eyes.y + 50),   # Bottom left
    pygame.K_7: (eyes.x - 50, eyes.y + 50),   # Bottom left
    pygame.K_8: (eyes.x - 50, eyes.y - 50),   # Top left
    pygame.K_9: (eyes.x + 0, eyes.y + 0),     # Center
}

# Define sounds for each key
sounds = {
    pygame.K_1: pygame.mixer.Sound('sounds_preset/Best show watched.mp3'),
    pygame.K_2: pygame.mixer.Sound('sounds_preset/Favorite fruit.mp3'),
    pygame.K_3: pygame.mixer.Sound('sounds_preset/Coffee tea or neither.mp3'),
    pygame.K_4: pygame.mixer.Sound('sounds_preset/Early bird or night owl.mp3'),
    pygame.K_5: pygame.mixer.Sound('sounds_preset/Favorite emojis.mp3'),
    pygame.K_6: pygame.mixer.Sound('sounds_preset/Breakfast question.mp3'),
    pygame.K_7: pygame.mixer.Sound('sounds_preset/Weekend activity.mp3'),
    pygame.K_8: pygame.mixer.Sound('sounds_preset/New skill.mp3'),
    pygame.K_9: pygame.mixer.Sound('sounds_preset/Favorite way to relax.mp3'),
}

# Initialize variables for delays and timing
move_delay = 0.5         # Delay before moving eyes
sound_delay = 1.5        # Additional delay after moving before sound plays
last_move_time = time.time()
last_interaction_time = time.time()
ready_for_sound = False  # Tracks if sound is ready to play
selected_key = None      # Track which key was last pressed

# Idle animation parameters
IDLE_DELAY = 5.0         # Time in seconds before idle animation starts
IDLE_RADIUS = 1.25       # Radius of the circular movement in pixels
IDLE_SPEED = 3.25        # Speed of the circular movement

def get_idle_offset(current_time):
    """Calculate idle position offset for subtle eye movement"""
    angle = (current_time * IDLE_SPEED) % (2 * math.pi)
    offset_x = IDLE_RADIUS * math.cos(angle)
    offset_y = IDLE_RADIUS * math.sin(angle)
    return offset_x, offset_y

running = True
while running:
    current_time = time.time()
    screen.fill((0,0,0))

    # Handle idle animation when no interaction has occurred recently
    time_since_interaction = current_time - last_interaction_time
    if time_since_interaction > IDLE_DELAY:
        offset_x, offset_y = get_idle_offset(current_time)
        current_x = pupil.x + offset_x
        current_y = pupil.y + offset_y
    else:
        current_x = pupil.x
        current_y = pupil.y
    
    # Draw 2 white circles (eyes)
    pygame.draw.circle(screen, (255,255,255), (eyes.x + 0, eyes.y + 0), 140) # (x,y) is the center of the circle
    pygame.draw.circle(screen, (255,255,255), (eyes.x + 375, eyes.y + 0), 140)

    # Draw 2 black circles (pupils) within the white circles
    pygame.draw.circle(screen, (0,0,0), (current_x + 0, current_y + 0), 40)
    pygame.draw.circle(screen, (0,0,0), (current_x + 375, current_y + 0), 40)

    # Check for key presses and update pupil position
    key = pygame.key.get_pressed()
    
    for k in pupil_positions:
        if key[k]:  # If a specific key is pressed
            new_x, new_y = pupil_positions[k]
            if current_time - last_move_time > move_delay:
                pupil.x, pupil.y = new_x, new_y  # Update pupil position
                last_move_time = current_time  # Reset the last move time
                last_interaction_time = current_time  # Reset idle timer
                ready_for_sound = True  # Enable sound delay
                selected_key = k  # Track which sound to play
                break

    # Play sound after the additional sound delay if movement occurred
    if ready_for_sound and current_time - last_move_time > sound_delay:
        if selected_key and selected_key in sounds:
            sounds[selected_key].play()
        ready_for_sound = False
    
    # Handle window events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.update()

pygame.quit()