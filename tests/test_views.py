import pytest
import shutil
from yamt.views import get_info
from yamt.views.dispatch_job import dispatch_backend
from .test_db import *
from .test_forms import created_dir, created_dir as created_dir_two
from yamt import encoding_queue

def test_dispatch_backend(db_add_settings, created_dir, created_dir_two):
    shutil.copyfile("london.mp4", created_dir / "london.mp4")
    # london.mp4 is a random movie test file i found on the interwebz
    assert dispatch_backend(1, created_dir / "london.mp4", created_dir_two)
    assert dispatch_backend(1, created_dir / "london.mp4", created_dir_two / "england.m4v")

    task1 = encoding_queue.get_nowait()
    task2 = encoding_queue.get_nowait()

    assert task1.input == created_dir / "london.mp4"
    assert task1.output == created_dir_two / "london.m4v"

    assert task2.input == created_dir / "london.mp4"
    assert task2.output == created_dir_two / "england.m4v"