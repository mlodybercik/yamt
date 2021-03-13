from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
from . import path_to_dir, PathField

class CreateFileWatch(FlaskForm):
    name = StringField("Watcher name:", validators=[DataRequired(), Length(max=32)])
    preset_name = SelectField("Settings preset:", validators=[DataRequired()])
    input_path = PathField("Input path to scan:", validators=[DataRequired(), path_to_dir])
    output_path = PathField("Output path:", validators=[DataRequired(), path_to_dir])