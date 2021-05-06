from wtforms.fields.simple import SubmitField
from yamt.pyffmpeg.ffmpeg_type.type_abbreviation import generate_choices_framerate, generate_choices_v_encoders,\
                                            generate_choices_a_encoders, generate_choices_presets
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import BooleanField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from . import positive_or_one


class CreateSettings(FlaskForm):
    preset_name = StringField("Preset name:", [DataRequired(), Length(max=32)])
    framerate_type = SelectField("Framerate cap:", [DataRequired()], choices=generate_choices_framerate(), default=0)
    v_encoder = SelectField("Video encoder:", [DataRequired()], choices=generate_choices_v_encoders())
    a_encoder = SelectField("Audio encoder:", [DataRequired()], choices=generate_choices_a_encoders())
    a_bitrate = IntegerField("Audio bitrate", [Optional(), positive_or_one])
    v_bitrate = IntegerField("Video bitrate", [Optional(), positive_or_one])
    a_samplerate = IntegerField("Audio samplerate", [Optional(), positive_or_one])
    preset = SelectField("Preset:", [Optional()], choices=generate_choices_presets(), default="medium")
    width = IntegerField("Width", [Optional(), positive_or_one])
    height = IntegerField("Height", [Optional(), positive_or_one])
    quality = IntegerField("Quality", [Optional(), positive_or_one])
    framerate = FloatField("Framerate", [Optional(), positive_or_one])
    web_optimise = BooleanField("Web optimise?", [Optional()])
    submit = SubmitField("Add")

