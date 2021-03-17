from .type_declarations import FRAMERATE_TYPE, V_ENCODERS, A_ENCODERS

# TODO: make fancy keys

def generate_choices_framerate():
    arr = []
    for item in FRAMERATE_TYPE.keys():
        arr.append((item, item))
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