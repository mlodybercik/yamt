import magic
import shlex
from dataclasses import dataclass, field
from pathlib import PosixPath as Path
from .type_declarations import SETTINGS, PositiveInteger, PositiveFloat, \
                               Size, DefaultPostInit, Preset

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
            if cls.__annotations__[item] == PositiveFloat:
                kwargs_copy[item] = PositiveFloat.init(value)
            elif cls.__annotations__[item] == PositiveInteger:
                kwargs_copy[item] = PositiveInteger.init(value)
        if "width" in kwargs and "height" in kwargs:
            kwargs_copy["size"] = Size(kwargs["width"], kwargs["height"])
        if "preset" in kwargs:
            if type(kwargs["preset"]) == str:
                kwargs_copy["preset"] = Preset(kwargs["preset"])
            
        kwargs.update(kwargs_copy)
        return cls(**kwargs)
        

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        logger.debug(f"Created settings: {self.__str__()}")

    def __str__(self):
        command = ""
        for name, type_ in self.__annotations__.items():
            value = self.__getattribute__(name)

            if type_ in [Size, Preset]:
                if (_ := str(value)):
                    command += str(value)
                else:
                    continue
            
            elif type_ == Path:
                command +=  f"{SETTINGS[name]} '{str(value)}'"

            elif type_ == bool:
                if value:
                    command += f"{SETTINGS[name]}"
                else:
                    continue

            elif type(SETTINGS[name]) == dict:
                command += SETTINGS[name][value]
            
            elif type_ == PositiveFloat and value == -1:
                continue

            elif type_ == PositiveInteger and value == -1:
                continue

            else:
                command += f"{SETTINGS[name]} {value}"

            command += " "
        return command

class ffmpegFullSettings(ffmpegSettings):
    input: Path = field(default_factory=Path)
    output: Path = field(default_factory=Path)

    def __init__(self, input: Path, output: Path, *args, **kwargs):
        self.input = input
        self.output = output
        self.__annotations__.update(super().__annotations__)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_settings(cls, settings: ffmpegSettings, input: Path, output: Path):
        kwargs = {}
        for name, _ in settings.__annotations__.items():
            kwargs[name] = settings.__getattribute__(name)
        return cls(input=input, output=output, **kwargs)

    def __post_init__(self):
        super().__post_init__()

    def __str__(self):
        # it has to be `-y` or it'll hang waiting on stdin
        command = f"ffmpeg -y -progress pipe:1 "
        return command + super().__str__()

TEST  = ffmpegSettings(widthxheight=Size(1280, 720))
TEST2 = ffmpegFullSettings.from_settings(TEST, Path("video.m4v"), Path("output.m4v"))

def is_video(filepath):
    return magic.from_file(filepath, mime=True).startswith("video")

def better_split(str):
    return shlex.split(str)