from flask import Blueprint, render_template, redirect
from . import logger, get_info
from ..pyffmpeg.ffmpeg_type.type_declarations import Signal
from .. import worker, watcher, kill_app, message_queue


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
