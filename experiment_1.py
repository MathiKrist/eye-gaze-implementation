import cv2
import pygame
import time
import math

class EyeSystem:
    def __init__(self, width=800, height=480):
        # Initialize Pygame and video capture
        pygame.init()
        pygame.mixer.init()
        self.cap = cv2.VideoCapture(0)
        
        # Screen setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Load face detection classifier
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        # Eye parameters
        self.eye_radius = 140
        self.pupil_radius = 40
        self.max_pupil_offset = 75
        
        # Base positions
        self.left_eye_pos = (217, 240)
        self.right_eye_pos = (217 + 375, 240)
        self.left_pupil_pos = list(self.left_eye_pos)
        self.right_pupil_pos = list(self.right_eye_pos)
        
        # Tracking mode parameters
        self.current_condition = 1  # Start with condition 1 (preset positions)
        self.movement_speed = 0.3
        
        # Preset position definitions
        self.preset_positions = {
            pygame.K_1: (self.left_eye_pos[0] + 50, self.left_eye_pos[1] + 50),   # Bottom right
            pygame.K_2: (self.left_eye_pos[0] + 50, self.left_eye_pos[1] + 50),   # Bottom right
            pygame.K_3: (self.left_eye_pos[0] - 75, self.left_eye_pos[1] + 0),    # Center left
            pygame.K_4: (self.left_eye_pos[0] + 75, self.left_eye_pos[1] + 0),    # Center right
            pygame.K_5: (self.left_eye_pos[0] + 0, self.left_eye_pos[1] - 75),    # Center top
            pygame.K_6: (self.left_eye_pos[0] - 50, self.left_eye_pos[1] + 50),   # Bottom left
            pygame.K_7: (self.left_eye_pos[0] - 50, self.left_eye_pos[1] + 50),   # Bottom left
            pygame.K_8: (self.left_eye_pos[0] - 50, self.left_eye_pos[1] - 50),   # Top left
            pygame.K_9: (self.left_eye_pos[0] + 0, self.left_eye_pos[1] + 0),     # Center
        }
        
        # Load both sets of sounds
        self.sounds_preset = {
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
        
        self.sounds_tracker = {
            pygame.K_1: pygame.mixer.Sound('sounds_tracker/Book recommendation.mp3'),
            pygame.K_2: pygame.mixer.Sound('sounds_tracker/Excited for christmas.mp3'),
            pygame.K_3: pygame.mixer.Sound('sounds_tracker/Family person.mp3'),
            pygame.K_4: pygame.mixer.Sound('sounds_tracker/Green or red apples.mp3'),
            pygame.K_5: pygame.mixer.Sound('sounds_tracker/Marathon.mp3'),
            pygame.K_6: pygame.mixer.Sound('sounds_tracker/Right or left handed.mp3'),
            pygame.K_7: pygame.mixer.Sound('sounds_tracker/Theme parks.mp3'),
            pygame.K_8: pygame.mixer.Sound('sounds_tracker/Wake up.mp3'),
            pygame.K_9: pygame.mixer.Sound('sounds_tracker/Winter or summer.mp3'),
        }
        
        # Timing control
        self.move_delay = 0.5
        self.sound_delay = 1.5
        self.last_move_time = 0
        self.last_interaction_time = time.time()
        self.ready_for_sound = False
        self.selected_key = None
        
        # Idle animation parameters
        self.IDLE_DELAY = 5.0
        self.IDLE_RADIUS = 1.25
        self.IDLE_SPEED = 3.25

    def get_idle_offset(self, current_time):
        """Calculate idle position offset for subtle eye movement"""
        angle = (current_time * self.IDLE_SPEED) % (2 * math.pi)
        offset_x = self.IDLE_RADIUS * math.cos(angle)
        offset_y = self.IDLE_RADIUS * math.sin(angle)
        return offset_x, offset_y

    def smooth_move(self, current_pos, target_pos):
        """Smoothly interpolate between positions"""
        return [current_pos[0] + (target_pos[0] - current_pos[0]) * self.movement_speed,
                current_pos[1] + (target_pos[1] - current_pos[1]) * self.movement_speed]

    def handle_input(self):
        """Handle keyboard input and mode switching"""
        current_time = time.time()
        keys = pygame.key.get_pressed()
        
        # Mode switching
        if keys[pygame.K_o]:  # Switch to condition 1 (preset positions)
            self.current_condition = 1
            print("Switched to Condition 1: Preset Positions")
        elif keys[pygame.K_t]:  # Switch to condition 2 (face tracking)
            self.current_condition = 2
            print("Switched to Condition 2: Face Tracking")
        
        # Sound triggering
        for k in range(pygame.K_1, pygame.K_9 + 1):
            if keys[k] and current_time - self.last_move_time > self.move_delay:
                self.last_move_time = current_time
                self.ready_for_sound = True
                self.selected_key = k
                self.last_interaction_time = current_time
                
                if self.current_condition == 1:
                    # Update pupil positions for preset mode
                    new_pos = self.preset_positions[k]
                    self.left_pupil_pos = list(new_pos)
                    self.right_pupil_pos = [new_pos[0] + 375, new_pos[1]]
                break
        
        # Play appropriate sound after delay
        if self.ready_for_sound and current_time - self.last_move_time > self.sound_delay:
            sounds = self.sounds_preset if self.current_condition == 1 else self.sounds_tracker
            if self.selected_key in sounds:
                sounds[self.selected_key].play()
            self.ready_for_sound = False

    def update_tracking(self):
        """Update eye positions based on face tracking (Condition 2)"""
        if self.current_condition != 2:
            return
            
        success, frame = self.cap.read()
        if not success:
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            frame_height, frame_width = frame.shape[:2]
            face_x = (x + w/2) / frame_width
            face_y = (y + h/2) / frame_height
            
            # Calculate eye movement
            x_direction = -(face_x - 0.5) * 2
            y_direction = (face_y - 0.5) * 2
            
            # Update target positions
            target_left = [
                self.left_eye_pos[0] + x_direction * self.max_pupil_offset,
                self.left_eye_pos[1] + y_direction * self.max_pupil_offset
            ]
            target_right = [
                self.right_eye_pos[0] + x_direction * self.max_pupil_offset,
                self.right_eye_pos[1] + y_direction * self.max_pupil_offset
            ]
            
            # Smooth movement
            self.left_pupil_pos = self.smooth_move(self.left_pupil_pos, target_left)
            self.right_pupil_pos = self.smooth_move(self.right_pupil_pos, target_right)

    def draw(self):
        """Draw the eyes and pupils"""
        current_time = time.time()
        self.screen.fill((0, 0, 0))
        
        # Apply idle animation in condition 1
        if self.current_condition == 1 and current_time - self.last_interaction_time > self.IDLE_DELAY:
            offset_x, offset_y = self.get_idle_offset(current_time)
            left_x = self.left_pupil_pos[0] + offset_x
            left_y = self.left_pupil_pos[1] + offset_y
            right_x = self.right_pupil_pos[0] + offset_x
            right_y = self.right_pupil_pos[1] + offset_y
        else:
            left_x, left_y = self.left_pupil_pos
            right_x, right_y = self.right_pupil_pos
        
        # Draw eyes
        pygame.draw.circle(self.screen, (255, 255, 255), self.left_eye_pos, self.eye_radius)
        pygame.draw.circle(self.screen, (255, 255, 255), self.right_eye_pos, self.eye_radius)
        
        # Draw pupils
        pygame.draw.circle(self.screen, (0, 0, 0), (int(left_x), int(left_y)), self.pupil_radius)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(right_x), int(right_y)), self.pupil_radius)
        
        pygame.display.update()

    def run(self):
        """Main program loop"""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update system
            self.handle_input()
            self.update_tracking()
            self.draw()
            
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    system = EyeSystem()
    system.run()