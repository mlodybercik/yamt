import logging
logger = logging.getLogger(__name__)
from flask import Blueprint, render_template, redirect
from .. import worker, watcher, kill_app
# from ..pyhandbrake import TEST2
# thats just for testing
    
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
    return render_template("main.html", worker=worker, watcher=watcher, worker_queue=worker_queue)

@main_view.route("/kill")
def kill():
    kill_app()
    return redirect("/")

@main_view.route("/test")
def test_asd():
    return render_template("test.html")