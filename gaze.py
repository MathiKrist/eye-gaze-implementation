import cv2
import numpy as np
from helpers import relative, relativeT

def gaze(frame, points):
    """
    The gaze function gets an image and face landmarks from the mediapipe framework.
    The function draws the gaze direction for both eyes into the frame.
    """

    # 2D image points for head pose estimation
    image_points = np.array([
        relative(points.landmark[4], frame.shape),  # Nose tip
        relative(points.landmark[152], frame.shape),  # Chin
        relative(points.landmark[263], frame.shape),  # Left eye left corner
        relative(points.landmark[33], frame.shape),  # Right eye right corner
        relative(points.landmark[287], frame.shape),  # Left Mouth corner
        relative(points.landmark[57], frame.shape)  # Right mouth corner
    ], dtype="double")

    # 3D image points for affine transformation
    image_points1 = np.array([
        relativeT(points.landmark[4], frame.shape),  # Nose tip
        relativeT(points.landmark[152], frame.shape),  # Chin
        relativeT(points.landmark[263], frame.shape),  # Left eye, left corner
        relativeT(points.landmark[33], frame.shape),  # Right eye, right corner
        relativeT(points.landmark[287], frame.shape),  # Left Mouth corner
        relativeT(points.landmark[57], frame.shape)  # Right mouth corner
    ], dtype="double")

    # 3D model points for head pose estimation
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0, -63.6, -12.5),  # Chin
        (-43.3, 32.7, -26),  # Left eye, left corner
        (43.3, 32.7, -26),  # Right eye, right corner
        (-28.9, -28.9, -24.1),  # Left Mouth corner
        (28.9, -28.9, -24.1)  # Right mouth corner
    ])

    # Eye ball centers
    Eye_ball_center_right = np.array([[-29.05], [32.7], [-39.5]])  # Right eye ball center
    Eye_ball_center_left = np.array([[29.05], [32.7], [-39.5]])  # Left eye ball center

    # Camera matrix estimation
    focal_length = frame.shape[1]
    center = (frame.shape[1] / 2, frame.shape[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                  dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    # 2D pupil locations for left and right eyes
    left_pupil = relative(points.landmark[468], frame.shape)
    right_pupil = relative(points.landmark[473], frame.shape)

    # Transformation between image points to world points
    _, transformation, _ = cv2.estimateAffine3D(image_points1, model_points)  # image to world transformation

    if transformation is not None:
        ### LEFT EYE GAZE ###
        pupil_world_cord_left = transformation @ np.array([[left_pupil[0], left_pupil[1], 0, 1]]).T
        S_left = Eye_ball_center_left + (pupil_world_cord_left - Eye_ball_center_left) * 10
        (eye_pupil2D_left, _) = cv2.projectPoints((int(S_left[0]), int(S_left[1]), int(S_left[2])), rotation_vector,
                                                  translation_vector, camera_matrix, dist_coeffs)
        (head_pose_left, _) = cv2.projectPoints((int(pupil_world_cord_left[0]), int(pupil_world_cord_left[1]), int(40)),
                                                rotation_vector, translation_vector, camera_matrix, dist_coeffs)
        gaze_left = left_pupil + (eye_pupil2D_left[0][0] - left_pupil) - (head_pose_left[0][0] - left_pupil)

        ### RIGHT EYE GAZE ###
        pupil_world_cord_right = transformation @ np.array([[right_pupil[0], right_pupil[1], 0, 1]]).T
        S_right = Eye_ball_center_right + (pupil_world_cord_right - Eye_ball_center_right) * 10
        (eye_pupil2D_right, _) = cv2.projectPoints((int(S_right[0]), int(S_right[1]), int(S_right[2])), rotation_vector,
                                                   translation_vector, camera_matrix, dist_coeffs)
        (head_pose_right, _) = cv2.projectPoints((int(pupil_world_cord_right[0]), int(pupil_world_cord_right[1]), int(40)),
                                                 rotation_vector, translation_vector, camera_matrix, dist_coeffs)
        gaze_right = right_pupil + (eye_pupil2D_right[0][0] - right_pupil) - (head_pose_right[0][0] - right_pupil)

        # Draw gaze line for left eye
        p1_left = (int(left_pupil[0]), int(left_pupil[1]))
        p2_left = (int(gaze_left[0]), int(gaze_left[1]))
        cv2.line(frame, p1_left, p2_left, (0, 0, 255), 2)  # Red line for left eye

        # Draw gaze line for right eye
        p1_right = (int(right_pupil[0]), int(right_pupil[1]))
        p2_right = (int(gaze_right[0]), int(gaze_right[1]))
        cv2.line(frame, p1_right, p2_right, (0, 255, 0), 2)  # Green line for right eye
