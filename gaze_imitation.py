import mediapipe as mp
import cv2
import pygame
import numpy as np
from helpers import relative, relativeT

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )
        
    def get_gaze_direction(self, frame, points):
        """Modified gaze function that returns normalized gaze directions instead of drawing"""
        # [Previous gaze calculation code remains the same until the final drawing section]
        image_points = np.array([
            relative(points.landmark[4], frame.shape),
            relative(points.landmark[152], frame.shape),
            relative(points.landmark[263], frame.shape),
            relative(points.landmark[33], frame.shape),
            relative(points.landmark[287], frame.shape),
            relative(points.landmark[57], frame.shape)
        ], dtype="double")

        image_points1 = np.array([
            relativeT(points.landmark[4], frame.shape),
            relativeT(points.landmark[152], frame.shape),
            relativeT(points.landmark[263], frame.shape),
            relativeT(points.landmark[33], frame.shape),
            relativeT(points.landmark[287], frame.shape),
            relativeT(points.landmark[57], frame.shape)
        ], dtype="double")

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0, -63.6, -12.5),
            (-43.3, 32.7, -26),
            (43.3, 32.7, -26),
            (-28.9, -28.9, -24.1),
            (28.9, -28.9, -24.1)
        ])

        Eye_ball_center_right = np.array([[-29.05], [32.7], [-39.5]])
        Eye_ball_center_left = np.array([[29.05], [32.7], [-39.5]])

        focal_length = frame.shape[1]
        center = (frame.shape[1] / 2, frame.shape[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1))
        (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                    dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

        left_pupil = relative(points.landmark[468], frame.shape)
        right_pupil = relative(points.landmark[473], frame.shape)

        _, transformation, _ = cv2.estimateAffine3D(image_points1, model_points)

        if transformation is not None:
            # Calculate gaze directions for both eyes
            pupil_world_cord_left = transformation @ np.array([[left_pupil[0], left_pupil[1], 0, 1]]).T
            S_left = Eye_ball_center_left + (pupil_world_cord_left - Eye_ball_center_left) * 10
            (eye_pupil2D_left, _) = cv2.projectPoints((int(S_left[0]), int(S_left[1]), int(S_left[2])), rotation_vector,
                                                     translation_vector, camera_matrix, dist_coeffs)
            (head_pose_left, _) = cv2.projectPoints((int(pupil_world_cord_left[0]), int(pupil_world_cord_left[1]), int(40)),
                                                   rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            gaze_left = left_pupil + (eye_pupil2D_left[0][0] - left_pupil) - (head_pose_left[0][0] - left_pupil)

            pupil_world_cord_right = transformation @ np.array([[right_pupil[0], right_pupil[1], 0, 1]]).T
            S_right = Eye_ball_center_right + (pupil_world_cord_right - Eye_ball_center_right) * 10
            (eye_pupil2D_right, _) = cv2.projectPoints((int(S_right[0]), int(S_right[1]), int(S_right[2])), rotation_vector,
                                                      translation_vector, camera_matrix, dist_coeffs)
            (head_pose_right, _) = cv2.projectPoints((int(pupil_world_cord_right[0]), int(pupil_world_cord_right[1]), int(40)),
                                                    rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            gaze_right = right_pupil + (eye_pupil2D_right[0][0] - right_pupil) - (head_pose_right[0][0] - right_pupil)

            # Return normalized gaze directions
            return (gaze_left - left_pupil) / frame.shape[1], (gaze_right - right_pupil) / frame.shape[1]
        return None, None

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
        self.movement_speed = 0.2  # Adjust this to control movement speed (0-1)

    def interpret_gaze(self, left_gaze, right_gaze):
        """Convert detected gaze into mirrored eye positions"""
        if left_gaze is None or right_gaze is None:
            # Return to center position if no gaze detected
            return (0, 0), (0, 0)
            
        # Average the gaze directions from both eyes
        #Horizontal movement
        avg_gaze_x = -(left_gaze[0] + right_gaze[0]) / 2  # Negative to mirror the direction
        #Vertical movement
        avg_gaze_y = (left_gaze[1] + right_gaze[1]) / 2  # Positive to not mirror the direction
        
        # Define thresholds for different directions
        threshold = 0.1
        
        # Convert continuous gaze into discrete positions
        x_direction = 0
        y_direction = 0
        
        if abs(avg_gaze_x) > threshold:
            x_direction = np.sign(avg_gaze_x)
        if abs(avg_gaze_y) > threshold:
            y_direction = np.sign(avg_gaze_y)
            
        return (x_direction, y_direction), (x_direction, y_direction)

    def smooth_move(self, current_pos, target_pos):
        """Smoothly interpolate between current and target position"""
        return [current_pos[0] + (target_pos[0] - current_pos[0]) * self.movement_speed,
                current_pos[1] + (target_pos[1] - current_pos[1]) * self.movement_speed]

    def update_pupils(self, left_gaze, right_gaze):
        # Get mirrored eye positions
        left_dir, right_dir = self.interpret_gaze(left_gaze, right_gaze)
        
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
            
        # Convert frame for face mesh
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = tracker.face_mesh.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Get gaze directions if face is detected
        if results.multi_face_landmarks:
            left_gaze, right_gaze = tracker.get_gaze_direction(frame, results.multi_face_landmarks[0])
            display.update_pupils(left_gaze, right_gaze)
        else:
            # Return to center if no face detected
            display.update_pupils(None, None)
        
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