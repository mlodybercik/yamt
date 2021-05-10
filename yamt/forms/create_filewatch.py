from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
from .validators import _path_to_dir
from . import _PathField, input_is_not_output

class CreateFileWatch(FlaskForm):
    name = StringField("Watcher name:", validators=[DataRequired(), Length(max=32)])
    preset_name = SelectField("Settings preset:", validators=[DataRequired()])
    input = _PathField("Input path to scan:", validators=[DataRequired(), _path_to_dir, input_is_not_output])
    output = _PathField("Output path:", validators=[DataRequired(), _path_to_dir])