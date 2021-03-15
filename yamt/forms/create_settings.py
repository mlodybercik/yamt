from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FloatField, RadioField, IntegerField, SelectField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

from ..pyhandbrake.type_declarations import FRAMERATE_TYPE, V_ENCODERS

class FloatRangeField(DecimalRangeField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0])
            except ValueError:
                raise ValueError("Not a propper float value.")

class CreateSettings(FlaskForm):
    preset_name = StringField("Preset name:", validators=[DataRequired(), Length(max=32)])
    v_encoder = SelectField("Video encoder:", choices=V_ENCODERS.keys(), validators=[DataRequired()], default="x264")
    a_encoder = StringField("Audio encoder:", validators=[DataRequired()], default="copy")
    optimise = BooleanField("Web optimise?")
    two_pass = BooleanField("Two pass?")
    width = IntegerField("Width:", validators=[DataRequired(), NumberRange(min=1, message="Weird size?")], render_kw={"placeholder": "1280"})
    height = IntegerField("Height:", validators=[DataRequired(), NumberRange(min=1, message="Weird size?")], render_kw={"placeholder": "720"})
    # TODO: create better way to add encoder settings, prepare for GPU acceleration and stuff
    adv_enc_settings = StringField("Adv. v_encoder settings (opt.):", default="")
    framerate_type = RadioField(choices=FRAMERATE_TYPE.keys(), default="VFR")
    framerate = FloatField("Framerate (opt.):", validators=[Optional(), NumberRange(min=1, message="Framerate should be >=1")])
    bitrate = IntegerField("Bitrate (opt.):", validators=[Optional(), NumberRange(min=1, message="Bitrate should be >=1")])
    quality = FloatRangeField("Quality: (opt.)", validators=[Optional(), NumberRange(min=0, max=51, message="0>=x>=51")], render_kw={"step":0.5, "min": 0, "max": 51, "style":"padding:0;"})
    # TODO: it should be quality or bitrate, not both.
