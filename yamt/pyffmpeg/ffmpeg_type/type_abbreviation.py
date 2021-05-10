from .type_declarations import FRAMERATE_TYPE, V_ENCODERS, A_ENCODERS, QUALITY_PRESET

FRAMERATE_TYPE_NAMES = {
    "PS": "Passthrough",
    "REGEN": "Discard frame timestamps",
    "CFR": "Constant framerate",
    "VFR": "Variable framerate",
    "AUTO": "Automaticly decide"
}

# TODO: fancy names

def generate_choices_framerate():
    arr = []
    for item in FRAMERATE_TYPE.keys():
        arr.append((item, FRAMERATE_TYPE_NAMES[item]))
    return arr

def generate_choices_v_encoders():
    arr = []
    for item in V_ENCODERS.keys():
        arr.append((item, item))
    return arr

def generate_choices_a_encoders():
    arr = []
    for item in A_ENCODERS.keys():
        arr.append((item, item))
    return arr

def generate_choices_presets():
    arr = []
    for item in QUALITY_PRESET:
        arr.append((item, item))
    return arr