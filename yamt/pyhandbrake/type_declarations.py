from enum import Enum
from pathlib import Path

PositiveInteger = int
PositiveFloat = float


FRAMERATE_TYPE = {
    "VFR": "--vfr",
    "CFR": "--cfr",
    "PFR": "--pfr"
}

SETTINGS = {
    "input": "-i",
    "output": "-o",
    "v_encoder": "-e",
    "optimise": "-O",
    "width": "-w",
    "height": "-l",
    "a_encoder": "-E",
    "adv_enc_settings": "-x",
    "framerate": "-r",
    "quality": "-q",
    "bitrate": "-b",
    "two_pass": "-2",
    "framerate_type": FRAMERATE_TYPE,
}

DATA_TYPES = {
    "input": Path,
    "output": Path,
    "v_encoder": str,
    "optimise": bool,
    "width": PositiveInteger,
    "height": PositiveInteger,
    "a_encoder": str,
    "adv_enc_settings": str,
    "framerate": PositiveFloat,
    "quality": PositiveInteger,
    "bitrate": PositiveInteger,
    "two_pass": bool,
    "framerate_type": str,
}

class State(Enum):
    UNKNOWN = None
    DEAD = 0
    WAITING = 1
    WORKING = 2