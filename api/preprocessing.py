import numpy as np

def preprocess_input(data) -> np.ndarray:
    gesture_map = {"hand_up": 0, "hand_wave": 1}
    action_map = {"still": 0, "moving": 1}
    location_map = {"bedroom_01": 0, "livingroom_01": 1}

    g = gesture_map.get(data.gesture, -1)
    a = action_map.get(data.prev_action, -1)
    l = location_map.get(data.device_id, -1)

    return np.array([l, g, a] + data.csi, dtype=float)
