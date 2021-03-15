from enum import Enum
from pathlib import Path

PositiveInteger = int
PositiveFloat = float


FRAMERATE_TYPE = {
    "VFR": "--vfr",
    "CFR": "--cfr",
    "PFR": "--pfr"
}

V_ENCODERS = {
    "x264": "-e x264",
    "x264@10bit": "-e x264_10bit",
    "x265": "-e x265",
    "x265@10bit": "-e x265_10bit",
    "x265@12bit": "-e x265_12bit",
    "MPEG4": "-e mpeg4",
    "MPEG2": "-e mpeg2", 
    "VP8": "-e VP8",
    "VP9": "-e VP9",
    "Theora": "-e theora",
}

# TODO: add more multiple choice settings, it should be pretty easy

SETTINGS = {
    "input": "-i",
    "output": "-o",
    "optimise": "-O",
    "width": "-w",
    "height": "-l",
    "a_encoder": "-E",
    "adv_enc_settings": "-x",
    "framerate": "-r",
    "bitrate": "-b",
    "two_pass": "-2",
    "quality": "-q",
    "v_encoder": V_ENCODERS,
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
    "quality": PositiveFloat,
    "bitrate": PositiveInteger,
    "two_pass": bool,
    "framerate_type": str,
}

class State(Enum):
    UNKNOWN = None
    DEAD = 0
    WAITING = 1
    WORKING = 2