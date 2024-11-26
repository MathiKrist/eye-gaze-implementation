import cv2
import pygame
import time

class EyeTracker:
    """
    Class responsible for face detection using OpenCV's Haarcascade classifier.
    This is a simpler alternative to MediaPipe, better suited for Raspberry Pi.
    """
    def __init__(self):
        # Load the pre-trained face detection classifier
        # Make sure this XML file is in the same directory as your script
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class EyeDisplay:
    """
    Class responsible for displaying animated eyes that follow face movement
    and handling sound playback based on key inputs.
    """
    def __init__(self, width=800, height=480):
        # Initialize Pygame for graphics and sound
        pygame.init()
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Define eye appearance parameters
        self.eye_radius = 140  # Size of the white part of the eye
        self.pupil_radius = 40  # Size of the black pupil
        self.max_pupil_offset = 75  # Maximum distance pupil can move from center
        
        # Set up initial positions for eyes and pupils
        # These values are optimized for an 800x480 display
        self.left_eye_pos = (217, 240)  # Center position of left eye
        self.right_eye_pos = (217 + 375, 240)  # Center position of right eye
        self.left_pupil_pos = list(self.left_eye_pos)  # Current position of left pupil
        self.right_pupil_pos = list(self.right_eye_pos)  # Current position of right pupil
        
        # Variables for smooth pupil movement
        self.target_left_pos = list(self.left_eye_pos)  # Target position for left pupil
        self.target_right_pos = list(self.right_eye_pos)  # Target position for right pupil
        self.movement_speed = 0.3  # Speed of pupil movement (0-1)

        # Manual control settings
        self.manual_control = False  # Flag for manual control mode
        self.manual_direction = (0, 0)  # Direction vector for manual control

        # Load sound files for interactive questions
        # Each sound is mapped to a number key (1-9)
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
        
        # Sound timing control variables
        self.move_delay = 0.5  # Delay before movement starts
        self.sound_delay = 1.5  # Delay before sound plays
        self.last_move_time = 0  # Timestamp of last movement
        self.ready_for_sound = False  # Flag indicating sound can be played
        self.selected_key = None  # Currently selected sound key

    def calculate_look_direction(self, face_position):
        """
        Calculate the direction the eyes should look based on face position.
        
        Args:
            face_position: Tuple of (x, y) coordinates of face in normalized space (0-1)
                         or None if no face detected
        
        Returns:
            Two tuples containing (x, y) direction vectors for left and right eyes
        """
        if self.manual_control:
            # In manual mode, both eyes use the same manual direction
            return self.manual_direction, self.manual_direction
            
        if face_position is None:
            # If no face detected, look straight ahead
            return (0, 0), (0, 0)
            
        face_x, face_y = face_position
        
        # Convert face position to direction vectors
        # Flip x-direction so eyes look at the face
        x_direction = -(face_x - 0.5) * 2
        y_direction = (face_y - 0.5) * 2
        
        return (x_direction, y_direction), (x_direction, y_direction)

    def smooth_move(self, current_pos, target_pos):
        """
        Smoothly interpolate between current and target positions.
        Creates more natural-looking eye movement.
        
        Args:
            current_pos: Current position [x, y]
            target_pos: Target position [x, y]
        
        Returns:
            New position [x, y] part way between current and target
        """
        return [current_pos[0] + (target_pos[0] - current_pos[0]) * self.movement_speed,
                current_pos[1] + (target_pos[1] - current_pos[1]) * self.movement_speed]

    def handle_key_press(self):
        """
        Handle keyboard input for manual control and sound playback.
        Arrow keys control manual mode and movement direction.
        Number keys trigger sound playback.
        """
        current_time = time.time()
        keys = pygame.key.get_pressed()
        
        # Handle arrow key controls for manual mode
        if keys[pygame.K_LEFT]:
            self.manual_control = True
            self.manual_direction = (-1, 0)  # Look left
        elif keys[pygame.K_RIGHT]:
            self.manual_control = True
            self.manual_direction = (1, 0)  # Look right
        elif keys[pygame.K_DOWN]:
            self.manual_control = False  # Return to face tracking
            self.manual_direction = (0, 0)
        elif keys[pygame.K_UP]:
            self.manual_control = True
            self.manual_direction = (0, 0)  # Look straight ahead
        
        # Check for sound trigger keys (1-9)
        for k in self.sounds.keys():
            if keys[k] and current_time - self.last_move_time > self.move_delay:
                self.last_move_time = current_time
                self.ready_for_sound = True
                self.selected_key = k
                break

        # Play sound after specified delay
        if self.ready_for_sound and current_time - self.last_move_time > self.sound_delay:
            if self.selected_key and self.selected_key in self.sounds:
                self.sounds[self.selected_key].play()
            self.ready_for_sound = False

    def update_pupils(self, face_position):
        """
        Update pupil positions based on face position or manual control.
        
        Args:
            face_position: Tuple of (x, y) coordinates of face in normalized space (0-1)
                         or None if no face detected
        """
        # Get eye directions based on face position or manual control
        left_dir, right_dir = self.calculate_look_direction(face_position)
        
        # Calculate target positions for pupils
        self.target_left_pos = [
            self.left_eye_pos[0] + left_dir[0] * self.max_pupil_offset,
            self.left_eye_pos[1] + left_dir[1] * self.max_pupil_offset
        ]
        self.target_right_pos = [
            self.right_eye_pos[0] + right_dir[0] * self.max_pupil_offset,
            self.right_eye_pos[1] + right_dir[1] * self.max_pupil_offset
        ]
        
        # Smoothly move pupils towards target positions
        self.left_pupil_pos = self.smooth_move(self.left_pupil_pos, self.target_left_pos)
        self.right_pupil_pos = self.smooth_move(self.right_pupil_pos, self.target_right_pos)

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

def main():
    """Main program loop"""
    # Initialize video capture from default camera (0)
    cap = cv2.VideoCapture(0)
    
    # Initialize face tracking and display components
    tracker = EyeTracker()
    display = EyeDisplay()
    
    running = True
    while running and cap.isOpened():
        # Get a frame from the camera
        success, frame = cap.read()
        if not success:
            print("Failed to get frame")
            continue
            
        # Convert frame to grayscale for face detection
        # Haarcascade works better with grayscale images
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        # Parameters: image, scale factor, min neighbors
        faces = tracker.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Process detected faces
        if len(faces) > 0 and not display.manual_control:
            # Get the first face detected (largest if multiple)
            (x, y, w, h) = faces[0]
            
            # Calculate relative position of face center in frame
            # Convert to normalized coordinates (0-1)
            frame_height, frame_width = frame.shape[:2]
            face_x = (x + w/2) / frame_width
            face_y = (y + h/2) / frame_height
            face_position = (face_x, face_y)
            
            # Update pupil positions based on face position
            display.update_pupils(face_position)
            
            # Draw rectangle around detected face (useful for debugging)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
        else:
            # No face detected or in manual mode
            display.update_pupils(None)
        
        # Handle keyboard input and sounds
        display.handle_key_press()
        
        # Update the display
        display.draw()
        
        # Show the camera feed (useful for debugging)
        cv2.imshow('Camera Feed', frame)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
        # Check for escape key press
        if cv2.waitKey(1) & 0xFF == 27:
            running = False
    
    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()