from utils import config

# ACTIONS:
[
    "LEFT_CLICK",
    "RIGHT_CLICK",
    "SCROLL",
    "TOGGLE_HOLD",
    "MIDDLE_CLICK",
    "MOUSE_CONTROL"
]

# HELPER FUNCTIONS
def dist(c1, c2):
    x1, y1 = c1
    x2, y2 = c2
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5

def is_close(fing):
    if fing[3][1] > fing[1][1]:
        return True
    return False

def is_open(fing):
    return not is_close(fing)


# GESTURE FUNCTION
def detect_gesture(kp_xy):
    thumb = kp_xy[1:5]
    index = kp_xy[5:9]
    middle = kp_xy[9:13]
    ring = kp_xy[13:17]
    pinky = kp_xy[17:]

    # PINCH GESTURES
    if dist(index[3], thumb[3]) < config.touch_threshold:
        return "LEFT_CLICK"
    if dist(middle[3], thumb[3]) < config.touch_threshold:
        return "RIGHT_CLICK"

    # CUSTOM GESTURES
    if is_open(index) and is_open(middle) and is_close(ring) and is_open(pinky):  # Ring curled
        return "SCROLL"
    if is_open(index) and is_close(middle) and is_open(ring) and is_open(pinky):  # Middle curled
        return "TOGGLE_HOLD"
    if is_open(index) and is_open(middle) and is_open(ring) and is_close(pinky):  # Pinky curled
        return "MIDDLE_CLICK"
    
    # PEACE / MOUSE MOVEMENT
    if is_open(index) and is_open(middle) and is_close(ring) and is_close(pinky):
        return "MOUSE_CONTROL"
    
    return None