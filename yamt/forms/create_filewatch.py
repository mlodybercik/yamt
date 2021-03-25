from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
from . import _path_to_dir, PathField, input_is_not_output

class CreateFileWatch(FlaskForm):
    name = StringField("Watcher name:", validators=[DataRequired(), Length(max=32)])
    preset_name = SelectField("Settings preset:", validators=[DataRequired()])
    input = PathField("Input path to scan:", validators=[DataRequired(), _path_to_dir, input_is_not_output])
    output = PathField("Output path:", validators=[DataRequired(), _path_to_dir])