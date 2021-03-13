import logging
logger = logging.getLogger(__name__)
from flask import Blueprint, render_template, redirect
from .. import worker, watcher, kill_app
    
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


# test

# @main_view.route("/test", methods=("GET", "POST"))
# def test_asd():
#     test = Test(meta={"csrf": False})
#     logger.debug(f"{watcher.is_alive()}")
#     if test.validate_on_submit():
#         return render_template("test.html", test=test)
#     else:
#         return render_template("test.html", test=test)