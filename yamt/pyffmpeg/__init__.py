import magic
import shlex
from dataclasses import dataclass, field
from pathlib import PosixPath as Path
from .type_declarations import SETTINGS, PositiveInteger, PositiveFloat, \
                               Size, DefaultPostInit, Preset
from ..forms import path_to_new_file_is_valid, path_to_file_is_valid

import logging
logger = logging.getLogger("pyffmpeg")

@dataclass
class ffmpegSettings:
    widthxheight: Size = Size(-1, -1)
    preset: Preset = Preset("medium")
    a_encoder: str = "COPY"
    a_bitrate: PositiveInteger = PositiveInteger(-1)
    a_samplerate: PositiveInteger = PositiveInteger(-1)
    web_optimise: bool = False
    v_encoder: str = "COPY"
    quality: PositiveInteger = PositiveInteger(30)
    # TODO: settings vary from encoder to encoder, ill propably need to create seperate
    #       dataclasses to hold any info eg. h264 vs nvenc_h264
    v_bitrate: PositiveInteger = PositiveInteger(-1)
    framerate_type: str = "AUTO"
    framerate: PositiveFloat = PositiveFloat(-1.0)

    @classmethod
    def init_from_unsure(cls, **kwargs):
        kwargs_copy = kwargs.copy()
        for item, value in kwargs.items():
            if item in cls.__annotations__:
                if cls.__annotations__[item] == PositiveFloat:
                    kwargs_copy[item] = PositiveFloat.init(value)
                elif cls.__annotations__[item] == PositiveInteger:
                    kwargs_copy[item] = PositiveInteger.init(value)
        if "width" in kwargs and "height" in kwargs:
            kwargs_copy["widthxheight"] = Size(kwargs["width"], kwargs["height"])
        if "preset" in kwargs:
            if type(kwargs["preset"]) == str:
                kwargs_copy["preset"] = Preset(kwargs["preset"])
            
        kwargs.update(kwargs_copy)
        kwargs = {x:kwargs[x] for x in kwargs if x in SETTINGS}
        return cls(**kwargs)
        

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        logger.debug(f"Created settings: {self.__str__()}")

    def __str__(self):
        command = ""
        for name, type_ in self.__annotations__.items():
            value = self.__getattribute__(name)

            if type_ in [Size, Preset]:
                if (value := str(value)):
                    command += value
                else:
                    continue

            elif type_ == bool:
                if value:
                    command += f"{SETTINGS[name]}"
                else:
                    continue

            elif type(SETTINGS[name]) == dict:
                command += SETTINGS[name][value]
            
            elif type_ in (PositiveFloat, PositiveInteger) and value == -1:
                continue

            else:
                command += f"{SETTINGS[name]} {value}"

            if not command.endswith(" "):
                command += " "
        return command.strip()

class ffmpegFullSettings(ffmpegSettings):
    input: Path = field(default_factory=Path)
    output: Path = field(default_factory=Path)
    settings: ffmpegSettings

    def __init__(self, settings: ffmpegSettings, input: Path, output: Path):
        self.input = input
        self.output = output
        self.settings = settings

    def __post_init__(self):
        if not path_to_file_is_valid(self.input) or not path_to_new_file_is_valid(self.output):
            raise AttributeError(f"Something is wrong with {self.input} or {self.output}")

    def __str__(self):
        # it has to be `-y` or it'll hang waiting on stdin
        command = f"ffmpeg -y -progress pipe:1 -i '{self.input}' {self.settings} '{self.output}'"
        return command

def is_video(filepath):
    return magic.from_file(filepath, mime=True).startswith("video")

def better_split(str):
    return shlex.split(str)