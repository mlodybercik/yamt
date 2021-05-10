import tempfile
import shutil
import pytest
import os
from pathlib import Path

from yamt.forms.validators import *

@pytest.fixture
def created_dir():
    with tempfile.TemporaryDirectory() as dir:
        yield Path(dir)

@pytest.fixture
def created_file(created_dir):
    temp_file = created_dir / "temp.txt"
    with open(temp_file, "w") as file:
        file.write("siemano kolano")
    return temp_file

def test_files(created_dir, created_file):
    assert path_to_dir_is_valid(created_dir)
    assert path_to_file_is_valid(created_file)
    assert path_to_new_file_is_valid(created_dir / "this_doesnt_exist.txt")
