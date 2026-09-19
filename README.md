# Gesture Controls

A Windows desktop mouse controller that uses a webcam and MediaPipe hand tracking to translate hand gestures into mouse movement, clicks, scrolling, and drag-and-drop control.

## Features

- Move the mouse with a two-finger gesture.
- Left, right, and middle click with pinch or finger gestures.
- Scroll vertically using the index and middle fingers.
- Toggle a held mouse button for drag-and-drop operations.
- Display hand landmarks, gesture status, confidence, and FPS in a live preview window.

## Requirements

- Windows
- Python 3.9 or newer
- A working webcam
- A display and mouse that PyAutoGUI can control

## Installation

1. Clone or download this project and open a terminal in its directory.

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Download the MediaPipe hand-landmarker model:

   ```powershell
   python download_handmarker.py
   ```

   This creates `hand_landmarker.task` in the project directory. The path must match `HANDMARKER_PATH` in `config.json`.

## Running

After installation, start the controller automatically with the included batch file. Double-click `run.bat`, or run it from PowerShell:

```powershell
.\run.bat
```

The script activates the local `.venv` environment and starts `main.py`. If you prefer to activate the environment yourself, run the controller directly from the project directory:

```powershell
python main.py
```

The webcam preview opens in a window named `MediaPipe Gesture Controller`. Make sure the camera is positioned so that your hand is visible and reasonably well lit.

### Keyboard controls

| Key | Action |
| --- | --- |
| `q` or `Esc` | Quit |
| `p` or `Space` | Pause until another key is pressed |
| `r` | Reload `config.json` |

## Gesture controls

Keep your hand inside the camera view. The controller uses the index fingertip as the reference point for movement and scrolling.

| Gesture | Action |
| --- | --- |
| Index and middle fingers open; ring and pinky curled | Mouse movement |
| Thumb and index fingertips pinched | Left click |
| Thumb and middle fingertips pinched | Right click |
| Index, middle, and pinky open; ring curled | Vertical scroll |
| Index, ring, and pinky open; middle curled | Toggle mouse hold for drag and drop |
| Index, middle, and ring open; pinky curled | Middle click |

Gestures are recognized in the order defined by `gestures.py`. Avoid making multiple fingertips touch at the same time, since pinch gestures take priority.

## Configuration

Edit `config.json` to tune tracking and input behavior. Press `r` in the preview window to reload the values without restarting.

| Setting | Default | Description |
| --- | ---: | --- |
| `CONF_THRESHOLD` | `0.3` | Minimum MediaPipe detection, presence, and tracking confidence |
| `FRAME_WIDTH` | `1280` | Requested camera frame width |
| `FRAME_HEIGHT` | `720` | Requested camera frame height |
| `TOUCH_THRESHOLD` | `25` | Maximum fingertip distance for a pinch gesture |
| `SENSITIVITY` | `10.8` | Mouse movement multiplier |
| `DEADZONE_RADIUS` | `10.0` | Movement deadzone around the gesture anchor |
| `SMOOTHING_FACTOR` | `0.05` | Mouse and scroll smoothing amount |
| `SCROLL_SENSITIVITY` | `0.5` | Scroll movement multiplier |
| `SCROLL_DEADZONE` | `8.0` | Scroll deadzone around the scroll anchor |
| `CLICK_COOLDOWN` | `0.35` | Seconds between click actions |
| `HOLD_COOLDOWN` | `0.60` | Seconds between hold-state toggles |
| `CAMERA_ID` | `0` | Camera device index |
| `HANDMARKER_PATH` | `hand_landmarker.task` | Path to the MediaPipe model file |

If the camera is not detected, try another `CAMERA_ID`, such as `1` or `2`.

## Project files

- `main.py` - Captures webcam frames, runs hand tracking, and controls the mouse.
- `gestures.py` - Defines fingertip and finger-position gesture detection.
- `utils.py` - Loads and exposes configuration values.
- `config.json` - Runtime settings.
- `download_handmarker.py` - Downloads the MediaPipe hand-landmarker model.
- `requirements.txt` - Python dependencies.
- `run.bat` - Activates `.venv` and starts the controller automatically.

## Safety notes

This program can move the pointer and send mouse input to any active application. Test it in a safe, empty area before using it with important documents or destructive actions. Keep the preview window accessible so you can quit with `Esc` or `q`, and do not leave the controller unattended while it is running.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for the full terms.
