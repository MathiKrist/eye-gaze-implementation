import mediapipe as mp
import cv2
import pygame
import numpy as np
import time

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )

    def get_gaze_position(self, points, frame_shape):
        """Calculate the position where the gaze intersects the screen"""
        # Get both irises
        left_iris = np.array([[points.landmark[idx].x * frame_shape[1],
                             points.landmark[idx].y * frame_shape[0]] 
                             for idx in [469, 470, 471, 472]])
        right_iris = np.array([[points.landmark[idx].x * frame_shape[1],
                              points.landmark[idx].y * frame_shape[0]] 
                              for idx in [474, 475, 476, 477]])

        # Calculate centers of both irises
        left_center = np.mean(left_iris, axis=0)
        right_center = np.mean(right_iris, axis=0)

        # Get eye corners for checking if eyes are open
        left_eye_corners = np.array([[points.landmark[idx].x * frame_shape[1],
                                    points.landmark[idx].y * frame_shape[0]]
                                    for idx in [263, 362]])  # Left eye corners
        right_eye_corners = np.array([[points.landmark[idx].x * frame_shape[1],
                                     points.landmark[idx].y * frame_shape[0]]
                                     for idx in [33, 133]])  # Right eye corners

        # Check if eyes are sufficiently open by measuring vertical distance
        left_eye_height = abs(points.landmark[386].y - points.landmark[374].y)
        right_eye_height = abs(points.landmark[159].y - points.landmark[145].y)
        
        # If eyes are too closed, return None
        if left_eye_height < 0.01 or right_eye_height < 0.01:
            return None

        # Use average of both iris positions to determine gaze point
        gaze_point = np.mean([left_center, right_center], axis=0)
        
        # Convert to normalized coordinates (0 to 1)
        gaze_x = gaze_point[0] / frame_shape[1]
        gaze_y = gaze_point[1] / frame_shape[0]

        return (gaze_x, gaze_y)

class EyeDisplay:
    def __init__(self, width=800, height=480):
        pygame.init()
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
        self.movement_speed = 0.2

    def calculate_look_direction(self, gaze_position):
        """Calculate where eyes should look based on gaze position"""
        if gaze_position is None:
            return (0, 0), (0, 0)  # Look straight ahead if no gaze detected
            
        gaze_x, gaze_y = gaze_position
        
        # Convert gaze position (0 to 1) to eye movement direction (-1 to 1)
        # Invert the direction so eyes look towards the gaze point
        x_direction = -(gaze_x - 0.5) * 2
        y_direction = (gaze_y - 0.5) * 2
        
        # Apply the same direction to both eyes
        return (x_direction, y_direction), (x_direction, y_direction)

    def smooth_move(self, current_pos, target_pos):
        """Smoothly interpolate between current and target position"""
        return [current_pos[0] + (target_pos[0] - current_pos[0]) * self.movement_speed,
                current_pos[1] + (target_pos[1] - current_pos[1]) * self.movement_speed]

    def update_pupils(self, gaze_position):
        # Get eye directions based on gaze position
        left_dir, right_dir = self.calculate_look_direction(gaze_position)
        
        if gaze_position is None:
            # Return to center if no gaze detected
            self.target_left_pos = list(self.left_eye_pos)
            self.target_right_pos = list(self.right_eye_pos)
        else:
            # Calculate target positions
            left_x, left_y = left_dir
            right_x, right_y = right_dir
            
            self.target_left_pos = [
                self.left_eye_pos[0] + left_x * self.max_pupil_offset,
                self.left_eye_pos[1] + left_y * self.max_pupil_offset
            ]
            self.target_right_pos = [
                self.right_eye_pos[0] + right_x * self.max_pupil_offset,
                self.right_eye_pos[1] + right_y * self.max_pupil_offset
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
            
        # Convert frame for face mesh
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = tracker.face_mesh.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Get gaze position if face is detected
        if results.multi_face_landmarks:
            gaze_position = tracker.get_gaze_position(results.multi_face_landmarks[0], frame.shape)
            display.update_pupils(gaze_position)
        else:
            # Return to center if no face detected
            display.update_pupils(None)
        
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