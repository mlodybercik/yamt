from dataclasses import dataclass
from pathvalidate import validate_filepath
from pathvalidate.error import ValidationError as pvValidationError
from pathvalidate.error import ErrorReason
from wtforms.validators import ValidationError as wtfValidationError
from typing import Union
from pathlib import Path

@dataclass
class DummyData:
    data: Union[str, Path]

def input_is_not_output(form, field):
    if form.input.data.resolve() == form.output.data.resolve():
        raise wtfValidationError("Input cant be the same as output!")

def positive_or_one(form, field):
    if field.data is not None:
        if field.data != -1 and field.data <= 0:
            raise wtfValidationError("Bad value!")

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

def path_to_file_is_valid(path: Union[str, Path]) -> bool:
    try:
        _path_to_file(None, DummyData(path))
        return True
    except wtfValidationError:
        return False

def path_to_dir_is_valid(path: Union[str, Path]) -> bool:
    try:
        _path_to_dir(None, DummyData(path))
        return True
    except wtfValidationError:
        return False

def path_to_new_file_is_valid(path: Union[str, Path]) -> bool:
    try:
        _path_to_new_file(None, DummyData(path))
        return True
    except wtfValidationError:
        return False

def _path_to_file(form, field):
    try:
        file_path = Path(field.data)
        if not file_path.exists() or file_path.is_dir():
            raise TypeError
    except TypeError:
        raise wtfValidationError("File doesnt exist.")
    bulk_path_validate(file_path, False)

def _path_to_dir(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.exists() or not dir_path.is_dir():
            raise TypeError
    except TypeError:
        raise wtfValidationError("Path doesnt exist.")
    bulk_path_validate(dir_path)

def _path_to_new_file(form, field):
    try:
        dir_path = Path(field.data)
        if not dir_path.parent.exists():
            raise TypeError
    except TypeError:
        raise wtfValidationError("Path doesnt exist.")
    bulk_path_validate(dir_path, False)