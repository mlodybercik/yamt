import logging
logger = logging.getLogger(__name__)
import magic
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from .type_declarations import SETTINGS, PositiveInteger, PositiveFloat

@dataclass
class HandbrakeSettings:
    """Settings class without input nor output paths"""
    width: PositiveInteger
    height: PositiveInteger
    adv_enc_settings: str = ""
    optimise: bool = False
    v_encoder: str = "x264"
    a_encoder: str = "copy"
    bitrate: int = -1
    quality: PositiveInteger = -1
    framerate: PositiveFloat = -1.0
    two_pass: bool = False
    framerate_type: str = ""

    def __post_init__(self):
        for name, type_ in self.__annotations__.items():
            if type(self.__getattribute__(name)) == dict:
                continue
            if issubclass(type(self.__getattribute__(name)), Path):
                continue
            assert type(self.__getattribute__(name)) == type_, f"{type(self.__getattribute__(name))} {name} {type_} {self.__getattribute__(name)}"
        logger.debug(f"Created settings: {self.__str__()}")

    def __str__(self):
        command = ""
        for name, type_ in self.__annotations__.items():
            # if bool, just insert corresponding switch
            if type_ == bool:
                command += f"{SETTINGS[name]}"
            # if string but empty then dont include it
            elif type_ == str and self.__getattribute__(name) == "":
                continue
            elif (type_ == PositiveInteger or type_ == PositiveFloat) and self.__getattribute__(name) == -1:
                continue
            elif name == "framerate_type":
                command += SETTINGS[name][self.__getattribute__(name)]
            elif type_ == Path:
                command += f"{SETTINGS[name]} '{str(self.__getattribute__(name))}'"
            else:
                command += f"{SETTINGS[name]} {self.__getattribute__(name)}"
            command += " "
        return command

    def split(self):
        # Failsafe
        return str(self).split()

class HandbrakeFullSettings(HandbrakeSettings):
    input: Path = field(default_factory=Path)
    output: Path = field(default_factory=Path)

    def __init__(self, input: Path, output: Path, *args, **kwargs):
        self.input = input
        self.output = output
        self.__annotations__.update(super().__annotations__)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_settings(cls, settings: HandbrakeSettings, input: Path, output: Path):
        kwargs = {}
        for name, _ in settings.__annotations__.items():
            kwargs[name] = settings.__getattribute__(name)
        return cls(input=input, output=output, **kwargs)

    def __post_init__(self):
        assert self.input  != ""
        assert self.output != ""
        assert self.input  != None
        assert self.output != None
        super().__post_init__()

    def __str__(self):
        command = f"HandBrakeCLI "
        return command + super().__str__()

TEST  = HandbrakeSettings(width=1280, height=720, adv_enc_settings="threads=1")
TEST2 = HandbrakeFullSettings.from_settings(TEST, Path("source"), Path("output"))

def is_video(filepath):
    return magic.from_file(filepath, mime=True).startswith("video")

def better_split(str):
    return shlex.split(str)