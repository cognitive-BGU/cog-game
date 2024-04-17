import numpy as np
from src.const import FRAME_WIDTH, FRAME_HEIGHT


def landmarks_to_cv(land):
    cv_x = land.x * FRAME_WIDTH
    cv_y = land.y * FRAME_HEIGHT
    cv_z = land.z * FRAME_WIDTH
    return {'x': cv_x, 'y': cv_y, 'z': cv_z}


def calculate_angle(a: dict, b: dict, c: dict):
    radians = np.arctan2(c['y'] - b['y'], c['x'] - b['x']) - np.arctan2(a['y'] - b['y'], a['x'] - b['x'])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def calculate_distance(pose1, pose2, landmarks, mp_pose):
    pose1_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose1].value])
    pose2_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose2].value])
    distance = np.sqrt((pose1_cv['x'] - pose2_cv['x']) ** 2 + (pose1_cv['y'] - pose2_cv['y']) ** 2)
    return distance


def calculate_center(pose1, pose2, landmarks, mp_pose):
    pose1_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose1].value])
    pose2_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose2].value])
    center = {'x': (pose1_cv['x'] + pose2_cv['x']) / 2, 'y': (pose1_cv['y'] + pose2_cv['y']) / 2}
    return center

def calculate_distance_from_coordinates(point1, point2):
    return np.sqrt((point1['x'] - point2['x']) ** 2 + (point1['y'] - point2['y']) ** 2)

def calculate_center_3d(pose1, pose2):
    #pose1_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose1].value])
    #pose2_cv = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[pose2].value])

    # Calculate the center for each dimension
    center = {
        'x': (pose1['x'] + pose2['x']) / 2,
        'y': (pose1['y'] + pose2['y']) / 2,
        'z': (pose1['z'] + pose2['z']) / 2
    }
    return center

def calculate_angle_3d(a: dict, b: dict, c: dict):
    # Convert points to numpy vectors
    vec_a = np.array([a['x'], a['y'], a['z']])
    vec_b = np.array([b['x'], b['y'], b['z']])
    vec_c = np.array([c['x'], c['y'], c['z']])

    # Calculate vectors BA and BC
    vec_ba = vec_a - vec_b
    vec_bc = vec_c - vec_b

    # Compute the cross product and dot product
    cross_prod = np.cross(vec_ba, vec_bc)
    dot_prod = np.dot(vec_ba, vec_bc)

    # Compute the angle using the arctan2 function
    angle = np.arctan2(np.linalg.norm(cross_prod), dot_prod)

    # Convert the angle to degrees
    angle_deg = np.abs(angle * 180.0 / np.pi)

    # Normalize the angle to be within 0 to 180 degrees
    if angle_deg > 180.0:
        angle_deg = 360 - angle_deg

    return angle_deg

def adjust_coor(pose1):
    return {'x': int(pose1['x'])*2, 'y': int(pose1['y'])*2, 'z': int(pose1['z'])*2}