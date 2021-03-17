from dataclasses import dataclass
from enum import Enum

class DefaultPostInit:
    def __post_init__(self):
        for name, type_ in self.__annotations__.items():
            assert type(self.__getattribute__(name)) == type_, f"Got {type(self.__getattribute__(name))} " + f"instead of {type_} {name}:{self.__getattribute__(name)} " + f"inside of {self.__class__}"

@dataclass
class Size:
    width: int
    height: int

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        if self.width <= 0 and self.width != -1:
            raise AttributeError("Width not in (0, +inf> u {-1}")
        if self.height <= 0 and self.height != -1:
            raise AttributeError("Height not in (0, +inf> u {-1}")

    def __str__(self):
        if self.width == -1 and self.height == -1:
            return ""
        else:
            return f"-filter:v {self.width}:{self.height}"

@dataclass
class PositiveInteger:
    value: int

    @classmethod
    def init(cls, value):
        return cls(int(value))

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        if self.value <= 0 and self.value != -1:
            raise AttributeError("Value not in (0, +inf> u {-1}")

    def __str__(self):
        return f"{self.value if self.value != -1 else ''}"

    def __eq__(self, o) -> bool:
        return o == self.value

@dataclass
class PositiveFloat:
    value: float

    @classmethod
    def init(cls, value):
        return cls(float(value))

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        if self.value <= 0 and self.value != -1:
            raise AttributeError("Value not in (0, +inf> u {-1}")
    
    def __str__(self):
        return f"{self.value if self.value != -1 else ''}"

    def __eq__(self, o) -> bool:
        return o == self.value
        

FRAMERATE_TYPE = {
    "PS": "-vsync 0",
    "REGEN": "-vsync drop",
    "CFR": "-vsync 1",
    "VFR": "-vsync 2",
    "AUTO": "-vsync -1",
}

V_ENCODERS = {
    # TODO: dynamicly create those settings
    "x264": "-c:v libx264",
    "x265": "-c:v libx265",
    "x264 NVENC": "-c:v nvenc_264",
    "x265 NVENC": "-c:v nvenc_hevc",
    "COPY": "-c:v copy",
}

A_ENCODERS = {
    # TODO: dynamicly create those settings
    "AAC": "-c:a aac",
    "FLAC": "-c:a flac",
    "MP3": "-c:a libmp3lame",
    "OPUS": "-c:a libopus",
    "COPY": "-c:a copy",
}

SETTINGS = {
    # TODO: add more settings
    "input": "-i",
    "output": "",
    "framerate": "-r",
    "a_bitrate": "-b:a",
    "a_samplerate": "-ar",
    "a_encoder": A_ENCODERS,
    "v_bitrate": "-b:v",
    "v_encoder": V_ENCODERS,
    "framerate_type": FRAMERATE_TYPE,
}

class State(Enum):
    UNKNOWN = None
    DEAD = 0
    WAITING = 1
    WORKING = 2