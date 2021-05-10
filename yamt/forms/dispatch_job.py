from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired
from . import _PathField, input_is_not_output
from .validators import _path_to_file, _path_to_new_file

class Start(FlaskForm):
    input = _PathField("File input:", validators=[DataRequired(), _path_to_file, input_is_not_output], render_kw={"placeholder": "eg. /test/video.mp4"})
    output = _PathField("File output:", validators=[DataRequired(), _path_to_new_file], render_kw={"placeholder": "eg. /test/video.mp4"})
    preset_name = SelectField("Preset:", choices=[], validators=[DataRequired()])
