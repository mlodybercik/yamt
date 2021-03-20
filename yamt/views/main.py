from flask import Blueprint, render_template, redirect
from .. import worker, watcher, kill_app, TEST, TEST2
from . import logger

main_view = Blueprint("main", __name__, template_folder="templates")

@main_view.route("/ping")
def hello():
    return "pong"

@main_view.route("/")
def index():
    # TODO: implement removing job from queue
    try:
        worker_queue = worker.queue.peek()
    except ValueError:
        worker_queue = []
    return render_template("main.html", worker=worker, watcher=watcher, worker_queue=worker_queue)

@main_view.route("/kill")
def kill():
    kill_app()
    return redirect("/")

@main_view.route("/test")
def test_asd():
    class Worker:
        settings_input = "/smb/xD/a co cie to/mov.mp4"
        settings_output = "/smb/xD/inna ścieżka/mov.m4v"
        queuepeek = [TEST2,TEST2,TEST2,TEST2,TEST2,TEST2]
        state_flag = "chuj ci na łeb"
        state = {'current_frame': 280, 'fps': 3.55, 'time_in_s': 7.566732, 'conversion_speed': '0.0959x', 'estimated': 32.94977485814498, 'percent': 70.72}

    class Watcher:
        state_flag = "chuj ci na łeb"

    return render_template("test.html", worker=Worker(), watcher=Watcher())