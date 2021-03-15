from wtforms.validators import ValidationError as wtfValidationError
from wtforms.fields import Field
from wtforms.widgets import TextInput
from pathlib import Path
from pathvalidate import validate_filepath
from pathvalidate.error import ValidationError as pvValidationError
from pathvalidate.error import ErrorReason

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

def bulk_path_validate(data, abs=True):
    try:
        validate_filepath(data, "Linux", check_reserved=True)
    except pvValidationError as e:
        if   e.reason == ErrorReason.INVALID_CHARACTER:
            raise wtfValidationError("Invalid character.")
        elif e.reason == ErrorReason.NULL_NAME:
            raise wtfValidationError("Can't be empty.")
        elif e.reason == ErrorReason.RESERVED_NAME:
            raise wtfValidationError("Reserved name.")
        elif e.reason == ErrorReason.FOUND_ABS_PATH and not abs:
            raise wtfValidationError("Absulute path?")
        elif e.reason == ErrorReason.MALFORMED_ABS_PATH and abs:
            raise wtfValidationError("Malformed absolute path.")

def positive_number(form, field):
    if field.data == None or field.data < 0:
        raise wtfValidationError("Number should be positive.")

def path_to_file(form, field):
    try:
        file_path = Path(field.data)
        if not file_path.exists() or file_path.is_dir():
            raise TypeError
    except TypeError:
        raise wtfValidationError("File doesnt exist.")
    bulk_path_validate(file_path, False)

def path_to_dir(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.exists() or not dir_path.is_dir():
            raise TypeError
    except TypeError:
        raise wtfValidationError("Path doesnt exist.")
    bulk_path_validate(dir_path)

def path_to_new_file(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.parent.exists():
            raise TypeError
    except TypeError:
        raise wtfValidationError("Path doesnt exist.")
    bulk_path_validate(dir_path, False)