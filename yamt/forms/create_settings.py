from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FloatField, RadioField, IntegerField
from wtforms.validators import DataRequired, Optional, Length
from . import positive_number


class CreateSettings(FlaskForm):
    preset_name = StringField("Preset name:", validators=[DataRequired(), Length(max=32)])
    v_encoder = StringField("Video encoder:", validators=[DataRequired()], default="x264", render_kw={"placeholder": "x264"})
    a_encoder = StringField("Audio encoder:", validators=[DataRequired()], default="copy")
    optimise = BooleanField("Web optimise?")
    two_pass = BooleanField("Two pass?")
    width = IntegerField("Width:", validators=[DataRequired(), positive_number], render_kw={"placeholder": "1280"})
    height = IntegerField("Height:", validators=[DataRequired(), positive_number], render_kw={"placeholder": "720"})
    adv_enc_settings = StringField("Adv. v_encoder settings (opt.):", default="")
    framerate_type = RadioField(choices=["CFR", "VFR", "PFR"], default="CFR")
    framerate = FloatField("Framerate (opt.):", validators=[Optional(), positive_number])
    bitrate = IntegerField("Bitrate (opt.):", validators=[Optional(), positive_number])
