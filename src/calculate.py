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



"""
global d, k
d, k = True, True
def update_hand_example(pos, org):
    global d,k
    change = 2
    length = 80
    if d:
        x = pos[0] - change
        y = (length ** 2 - (x - org[0]) ** 2) ** 0.5 + org[1]  # (x-a)^2 + (y-b)^2 = R
    else:
        x = pos[0] + change
        y = -(length ** 2 - (x - org[0]) ** 2) ** 0.5 + org[1]  # (x-a)^2 + (y-b)^2 = R

    if type(y) is complex:
        print("now")
        d = not d
        y = pos[1]
    
    if 712<x < 715:
        print(x,y)
        k = False
    if not k:
        x = pos[0] - change
        y = -(length ** 2 - (x - org[0]) ** 2) ** 0.5 + org[1]  # (x-a)^2 + (y-b)^2 = R
    
    return x, y
"""