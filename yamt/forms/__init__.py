from wtforms.validators import ValidationError
from wtforms.fields import Field
from wtforms.widgets import TextInput
from pathlib import Path

class PathField(Field):
    widget = TextInput()
    def _value(self):
        if self.data:
            return str(Path(self.data))
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = Path(valuelist[0])
        else:
            self.data = None

def positive_number(form, field):
    if field.data == None or field.data < 0:
        raise ValidationError("Number should be positive.")

def path_to_file(form, field):
    try:
        file_path = Path(field.data)
        if not file_path.exists() or file_path.is_dir():
            raise TypeError
    except TypeError:
        raise ValidationError("File doesnt exist.")

def path_to_dir(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.exists() or not dir_path.is_dir():
            raise TypeError
    except TypeError:
        raise ValidationError("Path doesnt exist.")

def path_to_new_file(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.parent.exists():
            raise TypeError
    except TypeError:
        raise ValidationError("Path doesnt exist.")