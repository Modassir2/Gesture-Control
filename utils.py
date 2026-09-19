import json

def load_config():
    try:
        with open(r".\config.json",'r') as f:
            return json.load(f)
    except (FileNotFoundError,json.JSONDecodeError) as e:
        print(f"An error occured loading config: {e}")
        print("Falling back to default values for all parameters.")
        return {
            "CONF_THRESHOLD" : 0.3,
            "FRAME_WIDTH" : 1280,
            "FRAME_HEIGHT" : 720,
            "TOUCH_THRESHOLD" : 25,

            "SENSITIVITY" : 10.8,
            "DEADZONE_RADIUS" : 10.0,
            "SMOOTHING_FACTOR" : 0.05,

            "SCROLL_SENSITIVITY" : 0.5,
            "SCROLL_DEADZONE" : 8.0,

            "CLICK_COOLDOWN" : 0.35,
            "HOLD_COOLDOWN" : 0.60,

            "CAMERA_ID": 0,
            "HANDMARKER_PATH":"hand_landmarker.task"
        }

class Config:
    def __init__(self):
        self.update()
    def update(self):
        d=load_config()
        self.conf= d.get("CONF_THRESHOLD",0.3)
        self.w = d.get("FRAME_WIDTH",1280)
        self.h = d.get("FRAME_HEIGHT",720)
        self.touch_threshold = d.get("TOUCH_THRESHOLD",25)
        self.sensi = d.get("SENSITIVITY",10.8)
        self.deadzone = d.get("DEADZONE_RADIUS" ,10)
        self.smooth_n = d.get("SMOOTHING_FACTOR", 0.05)
        self.scroll_sensi = d.get("SCROLL_SENSITIVITY", 0.5)
        self.deadzone_scroll = d.get("SCROLL_DEADZONE", 8.0)
        self.clk_cooldwn = d.get("CLICK_COOLDOWN", 0.35)
        self.hold_cooldown = d.get("HOLD_COOLDOWN", 0.60)
        self.path = d.get("HANDMARKER_PATH","hand_landmarker.task")
        self.cam = d.get("CAMERA_ID", 0)


config = Config()