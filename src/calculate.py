import numpy as np
from src.const import FRAME_WIDTH, FRAME_HEIGHT


def landmarks_to_cv(land):
    cv_x = land.x * FRAME_WIDTH
    cv_y = land.y * FRAME_HEIGHT
    return {'x': cv_x, 'y': cv_y}

def calculate_angle(a:dict, b:dict, c:dict):
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

"""
"""