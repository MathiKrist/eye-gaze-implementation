import pygame
import time

pygame.init
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

eyes = pygame.Rect(217,240,140,140) # (x,y,width,height)
pupil = pygame.Rect(217,240,40,40)

""" 
list of all the positions within the eye
center = (eyes.x + 0, eyes.y + 0),          # Center
bottom_right = (eyes.x + 50, eyes.y + 50),  # Bottom right
top_right = (eyes.x + 50, eyes.y -50),      # Top right
center_right = (eyes.x + 75, eyes.y + 0),   # Center right
center_top = (eyes.x + 0, eyes.y - 75),     # Center top
bottom_left = (eyes.x - 50, eyes.y + 50),   # Bottom left
center_left = (eyes.x - 75, eyes.y + 0),    # Center left
top_left = (eyes.x - 50, eyes.y - 50),      # Top left
center_bottom = (eyes.x + 0, eyes.y + 75),  # Center bottom
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

# Initialize variables for delays
move_delay = 0.5  # Delay before moving eyes
sound_delay = 1.5  # Additional delay after moving before sound plays
last_move_time = 0
ready_for_sound = False  # Tracks if sound is ready to play
selected_key = None  # Track which key was last pressed

running = True
while running:

    screen.fill((0,0,0))

    # Draw 2 white circles
    pygame.draw.circle(screen, (255,255,255), (eyes.x + 0, eyes.y + 0), 140) # (x,y) is the center of the circle
    pygame.draw.circle(screen, (255,255,255), (eyes.x + 375, eyes.y + 0), 140)

    # Draw 2 black circles within the white circles
    pygame.draw.circle(screen, (0,0,0), (pupil.x + 0, pupil.y + 0), 40) 
    pygame.draw.circle(screen, (0,0,0), (pupil.x + 375, pupil.y + 0), 40)

    # Check for key presses and update pupil position
    key = pygame.key.get_pressed()
    current_time = time.time()
    
    for k in pupil_positions:
        if key[k]:  # If a specific key is pressed
            new_x, new_y = pupil_positions[k]
            # Move pupil immediately if the required delay has passed
            if current_time - last_move_time > move_delay:
                pupil.x, pupil.y = new_x, new_y  # Update pupil position
                last_move_time = current_time  # Reset the last move time
                ready_for_sound = True  # Enable sound delay
                selected_key = k  # Track which sound to play
                break

    # Play sound after the additional sound delay if movement occurred
    if ready_for_sound and current_time - last_move_time > sound_delay:
        if selected_key and selected_key in sounds:
            sounds[selected_key].play()  # Play the sound for the selected key
        ready_for_sound = False  # Reset sound readiness
    
    # update the display
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.update()

pygame.quit()