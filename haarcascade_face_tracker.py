import cv2
import pygame
import time

class EyeTracker:
    def __init__(self):
        # Load the required trained XML classifier
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class EyeDisplay:
    def __init__(self, width=800, height=480):
        pygame.init()
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Eye parameters
        self.eye_radius = 140
        self.pupil_radius = 40
        self.max_pupil_offset = 75
        
        # Base positions for eyes and pupils
        self.left_eye_pos = (217, 240)
        self.right_eye_pos = (217 + 375, 240)
        self.left_pupil_pos = list(self.left_eye_pos)
        self.right_pupil_pos = list(self.right_eye_pos)
        
        # For smooth movement
        self.target_left_pos = list(self.left_eye_pos)
        self.target_right_pos = list(self.right_eye_pos)
        self.movement_speed = 0.3

        # Control mode
        self.manual_control = False
        self.manual_direction = (0, 0)  # (x, y) direction for manual control

        # Sounds for random questions
        self.sounds = {
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
        
        """
        # Sounds for experiment 2 picture 1
        self.sounds = {
            pygame.K_1: pygame.mixer.Sound('sounds_picture1/Green apples.mp3'),
            pygame.K_2: pygame.mixer.Sound('sounds_picture1/Basketballs.mp3'),
            pygame.K_3: pygame.mixer.Sound('sounds_picture1/Sentence problem.mp3'),
            pygame.K_4: pygame.mixer.Sound('sounds_picture1/Red apples.mp3'),
            pygame.K_5: pygame.mixer.Sound('sounds_picture1/Cats.mp3'),
            pygame.K_6: pygame.mixer.Sound('sounds_picture1/Math problem.mp3'),
            pygame.K_7: pygame.mixer.Sound('sounds_picture1/Oranges.mp3'),
            pygame.K_8: pygame.mixer.Sound('sounds_picture1/Dogs.mp3'),
        }
        """
        """
        # Sounds for experiment 2 picture 2
        self.sounds = {
            pygame.K_1: pygame.mixer.Sound('sounds_picture2/Blue circles.mp3'),
            pygame.K_2: pygame.mixer.Sound('sounds_picture2/Red squares.mp3'),
            pygame.K_3: pygame.mixer.Sound('sounds_picture2/Math problem.mp3'),
            pygame.K_4: pygame.mixer.Sound('sounds_picture2/Footballs.mp3'),
            pygame.K_5: pygame.mixer.Sound('sounds_picture2/Blueberries.mp3'),
            pygame.K_6: pygame.mixer.Sound('sounds_picture2/Red circles.mp3'),
            pygame.K_7: pygame.mixer.Sound('sounds_picture2/Sentence problem.mp3'),
            pygame.K_8: pygame.mixer.Sound('sounds_picture2/Strawberries.mp3'),
        }
        """
        
        # Sound timing
        self.move_delay = 0.5
        self.sound_delay = 1.5
        self.last_move_time = 0
        self.ready_for_sound = False
        self.selected_key = None

    def calculate_look_direction(self, face_position):
        """Calculate where eyes should look based on face position in frame"""
        if self.manual_control:
            return self.manual_direction, self.manual_direction
            
        if face_position is None:
            return (0, 0), (0, 0)  # Look straight ahead if no face detected
            
        face_x, face_y = face_position
        
        x_direction = -(face_x - 0.5) * 2
        y_direction = (face_y - 0.5) * 2
        
        return (x_direction, y_direction), (x_direction, y_direction)

    def smooth_move(self, current_pos, target_pos):
        """Smoothly interpolate between current and target position"""
        return [current_pos[0] + (target_pos[0] - current_pos[0]) * self.movement_speed,
                current_pos[1] + (target_pos[1] - current_pos[1]) * self.movement_speed]

    def handle_key_press(self):
        """Handle key presses for sound playback and manual control"""
        current_time = time.time()
        keys = pygame.key.get_pressed()
        
        # Handle arrow key controls
        if keys[pygame.K_LEFT]:
            self.manual_control = True
            self.manual_direction = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.manual_control = True
            self.manual_direction = (1, 0)
        elif keys[pygame.K_DOWN]:
            self.manual_control = False
            self.manual_direction = (0, 0)
        elif keys[pygame.K_UP]:
            self.manual_control = True
            self.manual_direction = (0, 0)
        
        # Check for sound trigger keys
        for k in self.sounds.keys():
            if keys[k] and current_time - self.last_move_time > self.move_delay:
                self.last_move_time = current_time
                self.ready_for_sound = True
                self.selected_key = k
                break

        # Play sound after delay
        if self.ready_for_sound and current_time - self.last_move_time > self.sound_delay:
            if self.selected_key and self.selected_key in self.sounds:
                self.sounds[self.selected_key].play()
            self.ready_for_sound = False

    def update_pupils(self, face_position):
        # Get eye directions based on face position or manual control
        left_dir, right_dir = self.calculate_look_direction(face_position)
        
        # Calculate target positions
        self.target_left_pos = [
            self.left_eye_pos[0] + left_dir[0] * self.max_pupil_offset,
            self.left_eye_pos[1] + left_dir[1] * self.max_pupil_offset
        ]
        self.target_right_pos = [
            self.right_eye_pos[0] + right_dir[0] * self.max_pupil_offset,
            self.right_eye_pos[1] + right_dir[1] * self.max_pupil_offset
        ]
        
        # Smoothly move towards target positions
        self.left_pupil_pos = self.smooth_move(self.left_pupil_pos, self.target_left_pos)
        self.right_pupil_pos = self.smooth_move(self.right_pupil_pos, self.target_right_pos)

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Draw eyes (white circles)
        pygame.draw.circle(self.screen, (255, 255, 255), self.left_eye_pos, self.eye_radius)
        pygame.draw.circle(self.screen, (255, 255, 255), self.right_eye_pos, self.eye_radius)
        
        # Draw pupils (black circles)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                         (int(self.left_pupil_pos[0]), int(self.left_pupil_pos[1])), 
                         self.pupil_radius)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                         (int(self.right_pupil_pos[0]), int(self.right_pupil_pos[1])), 
                         self.pupil_radius)
        
        pygame.display.update()

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    # Initialize our classes
    tracker = EyeTracker()
    display = EyeDisplay()
    
    running = True
    while running and cap.isOpened():
        # Process camera frame
        success, frame = cap.read()
        if not success:
            print("Failed to get frame")
            continue
            
        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using Haarcascade
        faces = tracker.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Get face position if face is detected and not in manual control
        if len(faces) > 0 and not display.manual_control:
            # Get the first face detected
            (x, y, w, h) = faces[0]
            # Calculate relative position of face center in frame
            frame_height, frame_width = frame.shape[:2]
            face_x = (x + w/2) / frame_width
            face_y = (y + h/2) / frame_height
            face_position = (face_x, face_y)
            display.update_pupils(face_position)
            
            # Draw rectangle around face (optional, for debugging)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
        else:
            display.update_pupils(None)
        
        # Handle key presses and sounds
        display.handle_key_press()
        
        # Draw the display
        display.draw()
        
        # Show the camera feed (optional, for debugging)
        cv2.imshow('Camera Feed', frame)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
        if cv2.waitKey(1) & 0xFF == 27:
            running = False
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()