from utils import config
from gestures import detect_gesture

import time
import os

import cv2
import mediapipe as mp
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0

# Screen resolution setup
SCREEN_W, SCREEN_H = pyautogui.size()

#SEKELETON CONNECTION
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# GLOBAL STATES
anchor_kp_pos = None # Reference (x, y) pixel coordinate when MOUSE_CONTROL starts
anchor_mouse_pos = None # Desktop mouse (x, y) coordinate when MOUSE_CONTROL starts
curr_target_x = None # Current smoothed X position
curr_target_y = None # Current smoothed Y position

anchor_scroll_y = None # Reference Y coordinate when SCROLL starts
curr_scroll_delta = 0.0 # Smoothed vertical delta for scrolling

is_holding = False # Tracks drag-and-drop state
last_click_time = 0 # Cooldown timer for clicks (left, right, middle)
last_hold_toggle_time = 0 # Cooldown timer for toggling hold state


# MEDIAPIPE INITIALIZATION
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


if not os.path.exists(config.path):
    print(f"Invalid 'HANDMARKER_PATH' path in config: {config.path}")
    print("Please download it by running `download_handmarker.py`.")
    exit(1)

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=config.path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=config.conf,
    min_hand_presence_confidence=config.conf,
    min_tracking_confidence=config.conf,
)


# MAIN PIPELINE
cap = cv2.VideoCapture(config.cam)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.h)

prev_time = time.time()
start_time = time.time()
last_timestamp_ms = -1

cv2.namedWindow("MediaPipe Gesture Controller", cv2.WINDOW_NORMAL)

try:
    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print(f"Error; CAMERA_ID: {config.cam} is not available")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            curr_time = time.time()
            time_diff = curr_time - prev_time
            fps = (1.0 / time_diff) if time_diff > 0 else 0.0
            prev_time = curr_time

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp_ms = max(last_timestamp_ms + 1, int((time.time() - start_time) * 1000))
            last_timestamp_ms = timestamp_ms
            
            results = landmarker.detect_for_video(mp_image, timestamp_ms)
            current_gesture = None

            if results.hand_landmarks:
                hand_landmarks = results.hand_landmarks[0]
                kp_xy = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

                min_x = min(pt[0] for pt in kp_xy)
                min_y = min(pt[1] for pt in kp_xy)
                max_x = max(pt[0] for pt in kp_xy)
                max_y = max(pt[1] for pt in kp_xy)

                box_conf = results.handedness[0][0].score

                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (255, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"CONF: {box_conf * 100:.2f}%",
                    (min_x + 5, max(min_y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 165, 255),
                    2,
                    cv2.LINE_AA
                )

                for id1, id2 in CONNECTIONS:
                    cv2.line(frame, kp_xy[id1], kp_xy[id2], (0, 255, 0), 3)

                for idx, pt in enumerate(kp_xy):
                    cv2.circle(frame, pt, 4, (0, 0, 255), -1)

                current_gesture = detect_gesture(kp_xy)
                ref_point_xy = kp_xy[8]  # Index Tip

                # 1. MOUSE MOVEMENT
                if current_gesture == "MOUSE_CONTROL":
                    if anchor_kp_pos is None:
                        anchor_kp_pos = ref_point_xy
                        anchor_mouse_pos = pyautogui.position()
                        curr_target_x, curr_target_y = float(anchor_mouse_pos[0]), float(anchor_mouse_pos[1])
                    else:
                        dx = ref_point_xy[0] - anchor_kp_pos[0]
                        dy = ref_point_xy[1] - anchor_kp_pos[1]
                        dist_from_anchor = (dx**2 + dy**2) ** 0.5

                        if dist_from_anchor < config.deadzone:
                            raw_target_x = anchor_mouse_pos[0]
                            raw_target_y = anchor_mouse_pos[1]
                        else:
                            raw_target_x = anchor_mouse_pos[0] + (dx * config.sensi)
                            raw_target_y = anchor_mouse_pos[1] + (dy * config.sensi)

                        curr_target_x = curr_target_x + (raw_target_x - curr_target_x) * config.smooth_n
                        curr_target_y = curr_target_y + (raw_target_y - curr_target_y) * config.smooth_n

                        clamped_x = max(0, min(SCREEN_W - 1, int(curr_target_x)))
                        clamped_y = max(0, min(SCREEN_H - 1, int(curr_target_y)))

                        pyautogui.moveTo(clamped_x, clamped_y)

                        cv2.circle(frame, anchor_kp_pos, int(config.deadzone), (0, 255, 255), 1)
                        cv2.circle(frame, anchor_kp_pos, 5, (255, 0, 255), -1)
                        cv2.line(frame, anchor_kp_pos, ref_point_xy, (255, 0, 255), 2)
                else:
                    anchor_kp_pos = None
                    anchor_mouse_pos = None
                    curr_target_x, curr_target_y = None, None

                # 2. VERTICAL SCROLLING
                if current_gesture == "SCROLL":
                    if anchor_scroll_y is None:
                        anchor_scroll_y = ref_point_xy[1]
                        curr_scroll_delta = 0.0
                    else:
                        raw_delta_y = ref_point_xy[1] - anchor_scroll_y

                        if abs(raw_delta_y) < config.deadzone_scroll:
                            target_delta = 0.0
                        else:
                            target_delta = -raw_delta_y * config.scroll_sensi

                        curr_scroll_delta += (target_delta - curr_scroll_delta) * config.smooth_n

                        if abs(curr_scroll_delta) > 0.1:
                            pyautogui.scroll(int(curr_scroll_delta))

                        anchor_pt = (ref_point_xy[0], anchor_scroll_y)
                        cv2.line(frame, anchor_pt, ref_point_xy, (0, 255, 255), 2)
                        cv2.circle(frame, anchor_pt, 4, (0, 255, 255), -1)
                else:
                    anchor_scroll_y = None
                    curr_scroll_delta = 0.0

                # 3. LEFT CLICK
                if current_gesture == "LEFT_CLICK":
                    if (curr_time - last_click_time) > config.clk_cooldwn:
                        pyautogui.click()
                        last_click_time = curr_time

                # 4. RIGHT CLICK
                elif current_gesture == "RIGHT_CLICK":
                    if (curr_time - last_click_time) > config.clk_cooldwn:
                        pyautogui.rightClick()
                        last_click_time = curr_time

                # 5. MIDDLE CLICK
                elif current_gesture == "MIDDLE_CLICK":
                    if (curr_time - last_click_time) > config.clk_cooldwn:
                        pyautogui.middleClick()
                        last_click_time = curr_time

                # 6. TOGGLE HOLD STATE
                if current_gesture == "TOGGLE_HOLD":
                    if (curr_time - last_hold_toggle_time) > config.hold_cooldown:
                        is_holding = not is_holding
                        if is_holding:
                            pyautogui.mouseDown()
                        else:
                            pyautogui.mouseUp()
                        last_hold_toggle_time = curr_time

            else:
                anchor_kp_pos = None
                anchor_mouse_pos = None
                curr_target_x, curr_target_y = None, None
                anchor_scroll_y = None
                curr_scroll_delta = 0.0

            if current_gesture or is_holding:
                gesture_text = f"GESTURE: {current_gesture if current_gesture else 'NONE'}"
                if is_holding:
                    gesture_text += " [MOUSE DOWN]"
                cv2.putText(
                    frame,
                    gesture_text,
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.imshow("MediaPipe Gesture Controller", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: # 'q' or escape=27
                print("User Quit")
                break
            elif key == ord('r'):
                config.update()
                print("Updated config")
            elif key == ord('p') or key == 32: # 'p' or spacebar=32
                print("Paused")
                cv2.waitKey(0)
                print("Resuming...")

except KeyboardInterrupt:
    print("Execution stopped by user.")

finally:
    print("Exiting...")
    if is_holding:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()