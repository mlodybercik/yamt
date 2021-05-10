import pytest
from yamt.pyffmpeg.stdqueue import RoundBuffer
from yamt.pyffmpeg import ffmpegSettings
from yamt.pyffmpeg.ffmpeg_type import *

def test_pyffmpeg_positive_integer():
    ten = PositiveInteger(10)
    mne = PositiveInteger(-1)

    assert str(ten) == "10"
    assert str(mne) == ""

    assert ten == PositiveInteger.init("10")
    assert mne == PositiveInteger.init("-1")

    with pytest.raises(TypeMismatch):
        PositiveInteger("-7")

    with pytest.raises(AttributeError):
        PositiveInteger(-7)

    with pytest.raises(AttributeError):
        PositiveInteger.init("-7")

def test_pyffmpeg_positive_float():
    ten = PositiveFloat(10.1)
    mne = PositiveFloat(-1.0)

    assert str(ten) == "10.1"
    assert str(mne) == ""

    assert ten == PositiveFloat.init("10.1")
    assert mne == PositiveFloat.init("-1.0")

    with pytest.raises(TypeMismatch):
        PositiveFloat("-7.1")

    with pytest.raises(TypeMismatch):
        PositiveFloat(-7)

    with pytest.raises(AttributeError):
        PositiveFloat(-7.1)

    with pytest.raises(AttributeError):
        PositiveFloat.init("-7.1")

def test_pyffmpeg_size():
    with pytest.raises(TypeMismatch):
        Size("-1", "-1")

    with pytest.raises(TypeMismatch):
        Size(10, "-1")

    with pytest.raises(TypeMismatch):
        Size("10", 10)

    with pytest.raises(AttributeError):
        Size(-20, -30)

    with pytest.raises(AttributeError):
        Size(20, -30)

    with pytest.raises(AttributeError):
        Size(-20, 30)

    assert str(Size(-1, -1)) == ""
    assert str(Size(10, 20)) == "-filter:v scale=10:20"

def test_pyffmpeg_preset():
    with pytest.raises(AttributeError):
        Preset("very slow")

    with pytest.raises(TypeMismatch):
        Preset(4)

    assert str(Preset("medium")) == ""
    assert str(Preset("veryslow")) == "-preset veryslow"

@pytest.fixture(scope="package")
def big_settings():
    yield ffmpegSettings(
        widthxheight=Size(128, 72),
        preset=Preset("veryslow"),
        a_encoder="AAC",
        a_bitrate=PositiveInteger(70000),
        a_samplerate=PositiveInteger(48000),
        web_optimise=True,
        v_encoder="x264",
        quality=PositiveInteger(20),
        v_bitrate=PositiveInteger(10000),
        framerate_type="REGEN",
        framerate=PositiveFloat(29.97))

def test_pyffmpeg_settings(big_settings):
    sett_str = str(big_settings)
    assert "-filter:v scale=128:72" in sett_str
    assert "-preset veryslow" in sett_str
    assert "-c:a aac" in sett_str
    assert "-b:a 70000" in sett_str
    assert "-ar 48000" in sett_str
    assert "-movflags +faststart" in sett_str
    assert "-c:v libx264" in sett_str
    assert "-crf 20" in sett_str
    assert "-b:v 10000" in sett_str
    assert "-vsync drop" in sett_str
    assert "-r 29.97" in sett_str

    assert ffmpegSettings(widthxheight=Size(100, 10)) == ffmpegSettings.init_from_unsure(width = 100, height = 10)
    assert ffmpegSettings(preset=Preset("slow")) == ffmpegSettings.init_from_unsure(preset="slow")

def test_observer():
    # TODO: is there even a nice way to do it?
    pytest.skip()

def test_pyffmpeg_stdqueue():
    buff = RoundBuffer(4)
    for item in range(7):
        buff.append(item)
    assert buff.dump_list() == [3, 4, 5, 6]
    assert buff.find_and_return_slice(lambda a: True if a==3 else False, 2) == [3, 4]
    assert buff.find_and_return_slice(lambda a: True if a==4 else False, 2) == [4, 5]
