from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from . import path_to_file, path_to_new_file, PathField

class Start(FlaskForm):
    input = PathField("File input:", validators=[DataRequired(), path_to_file], render_kw={"placeholder": "eg. /test/video.mp4"})
    output = PathField("File output:", validators=[DataRequired(), path_to_new_file], render_kw={"placeholder": "eg. /test/video.mp4"})
    preset_name = SelectField("Preset:", choices=[], validators=[DataRequired()])

# test

class Test(FlaskForm):
    file = PathField("File:", validators=[DataRequired()])