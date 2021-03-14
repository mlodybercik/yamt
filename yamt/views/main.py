import logging
logger = logging.getLogger(__name__)
from flask import Blueprint, render_template, redirect
from .. import worker, watcher, kill_app
from ..pyhandbrake import TEST2
    
main_view = Blueprint("main", __name__, template_folder="templates")

@main_view.route("/ping")
def hello():
    return "pong"

@main_view.route("/")
def index():
    return render_template("main.html", worker=worker, watcher=watcher)

@main_view.route("/kill")
def kill():
    kill_app()
    return redirect("/")

@main_view.route("/test")
def test_asd():
    class test_worker:
        state_flag = "working"
        state = (74.32, 0, 0, 0)
        queuepeek = [TEST2,TEST2,TEST2,TEST2]
        settings_input = "/smb/all/jakaś ścieżka/london.mp4"
        settings_output = "/smb/all/jakaś inna ścieżka/london.m4v"


    class test_watcher:
        state_flag = "working"

    return render_template("test.html", worker=test_worker(), watcher=test_watcher)