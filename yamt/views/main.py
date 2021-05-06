from flask import Blueprint, render_template, redirect, request, jsonify
from . import logger, get_info
from ..pyffmpeg import Path, Size, ffmpegFullSettings, ffmpegSettings
from ..pyffmpeg.ffmpeg_type.type_declarations import Signal
from .. import worker, watcher, kill_app, flash_exception, message_queue


main_view = Blueprint("main", __name__, template_folder="templates")

@main_view.route("/ping")
def hello():
    return "pong"

@main_view.route("/")
def index():
    try:
        worker_queue = worker.queue.peek()
    except ValueError:
        worker_queue = []
    info = get_info()
    return render_template("main.html", worker=worker, watcher=watcher, worker_queue=worker_queue, info=info)

@main_view.route("/kill")
def kill():
    kill_app()
    return redirect("/")

@main_view.route("/get_update")
def get_update():
    data = {
        "curr_task": worker.state,
        "states": [worker.state_flag.value, watcher.state_flag.value],
        "cpu": get_info(),
    }
    return data

@main_view.route("/pause", methods=["POST"])
def pause():
    message_queue.put(Signal.PAUSE)
    return "ok"

@main_view.route("/stop", methods=["POST"])
def stop():
    message_queue.put(Signal.STOP)
    return "ok"

TEST  = ffmpegSettings(widthxheight=Size(1280, 720), v_encoder="x264")
TEST2 = ffmpegFullSettings(settings=TEST, input=Path("london.mp4"), output=Path("london.m4v"))

# Website testing purposes
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

    def x():
        x()

    try:
        x()
    except RecursionError as x:
        flash_exception(x)
    
    return render_template("test.html", worker=Worker(), watcher=Watcher())
