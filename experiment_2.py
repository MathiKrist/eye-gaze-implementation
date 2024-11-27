import cv2
import pygame
import time

class EyeSystem:
    """
    Eye tracking system for picture experiment with two conditions:
    1. Questions triggered when looking back at robot (sounds_picture1)
    2. Questions triggered while looking at screen (sounds_picture2)
    
    Features:
    - Face tracking in both conditions
    - Manual control with arrow keys
    - Two different sound sets for different conditions
    - Dead stare functionality
    
    Controls:
    - 'o': Switch to Condition 1
    - 't': Switch to Condition 2
    - Arrow keys: Manual eye control
    - Keys 1-8: Trigger sounds based on current condition
    """
    def __init__(self, width=800, height=480):
        # Initialize pygame and webcam
        pygame.init()
        pygame.mixer.init()             # Required for sound playback
        self.cap = cv2.VideoCapture(0)  # Initialize webcam
        
        # Load face detection classifier for tracking
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        # Screen setup - optimized for 800x480 display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Eye appearance parameters
        self.eye_radius = 140       # Size of the white part of the eye
        self.pupil_radius = 40      # Size of the black pupil
        self.max_pupil_offset = 80  # Maximum distance pupil can move from center
        
        # Define base positions for eyes and pupils
        self.left_eye_pos = (217, 240)                   # Center position of left eye
        self.right_eye_pos = (217 + 375, 240)            # Center position of right eye (375px offset)
        self.left_pupil_pos = list(self.left_eye_pos)    # Current position of left pupil
        self.right_pupil_pos = list(self.right_eye_pos)  # Current position of right pupil
        
        # Control and movement settings
        self.current_condition = 1      # Start with condition 1
        self.manual_control = False     # Flag for manual control mode
        self.manual_direction = (0, 0)  # Direction vector for manual control
        self.movement_speed = 0.3       # Speed of pupil movement (0-1)
        
        # Load sound sets for both conditions
        # Condition 1: Questions when looking back at robot
        self.sounds_condition1 = {
            pygame.K_1: pygame.mixer.Sound('sounds_picture1/Green apples.mp3'),
            pygame.K_2: pygame.mixer.Sound('sounds_picture1/Basketballs.mp3'),
            pygame.K_3: pygame.mixer.Sound('sounds_picture1/Sentence problem.mp3'),
            pygame.K_4: pygame.mixer.Sound('sounds_picture1/Red apples.mp3'),
            pygame.K_5: pygame.mixer.Sound('sounds_picture1/Cats.mp3'),
            pygame.K_6: pygame.mixer.Sound('sounds_picture1/Math problem.mp3'),
            pygame.K_7: pygame.mixer.Sound('sounds_picture1/Oranges.mp3'),
            pygame.K_8: pygame.mixer.Sound('sounds_picture1/Dogs.mp3'),
        }
        
        # Condition 2: Questions while looking at screen
        self.sounds_condition2 = {
            pygame.K_1: pygame.mixer.Sound('sounds_picture2/Blue circles.mp3'),
            pygame.K_2: pygame.mixer.Sound('sounds_picture2/Red squares.mp3'),
            pygame.K_3: pygame.mixer.Sound('sounds_picture2/Math problem.mp3'),
            pygame.K_4: pygame.mixer.Sound('sounds_picture2/Footballs.mp3'),
            pygame.K_5: pygame.mixer.Sound('sounds_picture2/Blueberries.mp3'),
            pygame.K_6: pygame.mixer.Sound('sounds_picture2/Red circles.mp3'),
            pygame.K_7: pygame.mixer.Sound('sounds_picture2/Sentence problem.mp3'),
            pygame.K_8: pygame.mixer.Sound('sounds_picture2/Strawberries.mp3'),
        }
        
        # Timing control variables
        self.move_delay = 0.5         # Delay before movement starts
        self.sound_delay = 1.5        # Delay before sound plays after movement
        self.last_move_time = 0       # Timestamp of last movement
        self.ready_for_sound = False  # Flag indicating sound can be played
        self.selected_key = None      # Currently selected sound key

    def handle_input(self):
        """
        Handle all keyboard input including:
        - Condition switching with 'o' and 't'
        - Manual control with arrow keys
        - Sound triggering with number keys 1-8
        """
        current_time = time.time()
        keys = pygame.key.get_pressed()
        
        # Condition switching
        if keys[pygame.K_o]:    # Switch to condition 1 (questions when looking back)
            self.current_condition = 1
            print("Switched to Condition 1: Questions on looking back")
        elif keys[pygame.K_t]:  # Switch to condition 2 (questions while looking)
            self.current_condition = 2
            print("Switched to Condition 2: Questions while looking at screen")
            
        # Manual eye control with arrow keys
        if keys[pygame.K_LEFT]:
            self.manual_control = True
            self.manual_direction = (-1, 0)  # Look left
        elif keys[pygame.K_RIGHT]:
            self.manual_control = True
            self.manual_direction = (1, 0)   # Look right
        elif keys[pygame.K_UP]:
            self.manual_control = True
            self.manual_direction = (0, 0)   # Dead stare (center position) - if needed
        elif keys[pygame.K_DOWN]:
            self.manual_control = False      # Return to face tracking mode
            
        # Sound triggering based on current condition
        sounds = self.sounds_condition1 if self.current_condition == 1 else self.sounds_condition2
        for k in sounds.keys():
            if keys[k] and current_time - self.last_move_time > self.move_delay:
                self.last_move_time = current_time
                self.ready_for_sound = True
                self.selected_key = k
                break
        
        # Play sound after specified delay
        if self.ready_for_sound and current_time - self.last_move_time > self.sound_delay:
            if self.selected_key and self.selected_key in sounds:
                sounds[self.selected_key].play()
            self.ready_for_sound = False

    def update_tracking(self):
        """
        Update eye positions based on face tracking or manual control.
        Face tracking is active when manual_control is False.
        Returns the processed frame (unused in this version).
        """
        success, frame = self.cap.read()
        if not success:
            return None
            
        # Process frame for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Calculate direction for eye movement
        if len(faces) > 0 and not self.manual_control:
            # Face detected and in tracking mode
            (x, y, w, h) = faces[0]
            frame_height, frame_width = frame.shape[:2]
            face_x = (x + w/2) / frame_width
            face_y = (y + h/2) / frame_height
            
            # Convert face position to direction vectors
            x_direction = -(face_x - 0.5) * 2  # Invert x so eyes look at face
            y_direction = (face_y - 0.5) * 2
        elif self.manual_control:
            # Use manual direction if in manual control mode
            x_direction, y_direction = self.manual_direction
        else:
            # No face detected and not in manual mode - look straight ahead
            x_direction, y_direction = 0, 0
            
        # Calculate target positions for pupils
        target_left = [
            self.left_eye_pos[0] + x_direction * self.max_pupil_offset,
            self.left_eye_pos[1] + y_direction * self.max_pupil_offset
        ]
        target_right = [
            self.right_eye_pos[0] + x_direction * self.max_pupil_offset,
            self.right_eye_pos[1] + y_direction * self.max_pupil_offset
        ]
        
        # Smooth movement towards target positions
        self.left_pupil_pos = [
            self.left_pupil_pos[0] + (target_left[0] - self.left_pupil_pos[0]) * self.movement_speed,
            self.left_pupil_pos[1] + (target_left[1] - self.left_pupil_pos[1]) * self.movement_speed
        ]
        self.right_pupil_pos = [
            self.right_pupil_pos[0] + (target_right[0] - self.right_pupil_pos[0]) * self.movement_speed,
            self.right_pupil_pos[1] + (target_right[1] - self.right_pupil_pos[1]) * self.movement_speed
        ]
        
        return frame

    def draw(self):
        """Draw the eyes and pupils on the screen"""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Draw the white part of the eyes
        pygame.draw.circle(self.screen, (255, 255, 255), self.left_eye_pos, self.eye_radius)
        pygame.draw.circle(self.screen, (255, 255, 255), self.right_eye_pos, self.eye_radius)
        
        # Draw the black pupils
        pygame.draw.circle(self.screen, (0, 0, 0), 
                         (int(self.left_pupil_pos[0]), int(self.left_pupil_pos[1])), 
                         self.pupil_radius)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                         (int(self.right_pupil_pos[0]), int(self.right_pupil_pos[1])), 
                         self.pupil_radius)
        
        # Update the display
        pygame.display.update()

    def run(self):
        """
        Main program loop.
        Handles events, updates tracking, and draws eyes until program is closed.
        """
        running = True
        while running:
            # Process window and keyboard events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update system state
            self.handle_input()
            self.update_tracking()
            self.draw()
        
        # Cleanup resources when done
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    system = EyeSystem()
    system.run()