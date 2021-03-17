import logging
logger = logging.getLogger(__name__)
import magic
import shlex
from dataclasses import dataclass, field
from pathlib import PosixPath as Path
from .type_declarations import SETTINGS, PositiveInteger, PositiveFloat, \
                               Size, DefaultPostInit


@dataclass
class ffmpegSettings:
    widthxheight: Size = Size(-1, -1)
    a_encoder: str = "COPY"
    a_bitrate: PositiveInteger = PositiveInteger(-1)
    a_samplerate: PositiveInteger = PositiveInteger(-1)
    v_encoder: str = "COPY"
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
            kwargs["size"] = Size(kwargs["width"], kwargs["height"])
            
        kwargs.update(kwargs_copy)
        return cls(**kwargs)
        

    def __post_init__(self):
        DefaultPostInit.__post_init__(self)
        logger.debug(f"Created settings: {self.__str__()}")

    def __str__(self):
        command = ""
        for name, type_ in self.__annotations__.items():
            value = self.__getattribute__(name)

            if type_ == Size:
                if (_ := str(value)):
                    command += str(value)
                else:
                    continue
            
            elif type_ == Path:
                command +=  f"{SETTINGS[name]} '{str(value)}'"
            
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
        assert self.input not in ["", None]
        assert self.output not in ["", None]
        super().__post_init__()

    def __str__(self):
        # it has to be `-y` or itll hang
        command = f"ffmpeg -y -progress pipe:0"
        return command + super().__str__()

TEST = ffmpegSettings(widthxheight=Size(1280, 720))

def is_video(filepath):
    return magic.from_file(filepath, mime=True).startswith("video")

def better_split(str):
    return shlex.split(str)