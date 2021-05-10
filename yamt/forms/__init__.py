from wtforms.fields import Field
from wtforms.widgets import TextInput
from pathlib import Path

class _PathField(Field):
    widget = TextInput()
    def _value(self):
        return self.data if self.data else ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = Path(valuelist[0]).resolve()
        else:
            self.data = None

from .validators import input_is_not_output, path_to_dir_is_valid, path_to_file_is_valid, \
                        path_to_new_file_is_valid, positive_or_one

from .create_filewatch import CreateFileWatch
from .create_settings import CreateSettings
from .dispatch_job import Start

__all__ = [input_is_not_output, path_to_dir_is_valid, path_to_file_is_valid, \
           path_to_new_file_is_valid, positive_or_one, CreateFileWatch, CreateSettings, Start]