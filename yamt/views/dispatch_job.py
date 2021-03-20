from pathlib import Path
from flask import Blueprint, render_template, redirect, request
from flask.helpers import flash, url_for
from jinja2 import Markup, escape
from . import logger
from ..models import Settings
from ..forms.dispatch_job import Start
from ..pyffmpeg import ffmpegFullSettings
from .. import worker

dispatch_job = Blueprint("dispatch_job", __name__, template_folder="templates")

def dispatch_backend(preset_id: int, input: Path, output: Path):
    if output.is_dir(): #TODO: create another way to check for datatypes not using wtform
        print("is dir") #FIXME: this is veeeeery ugly
        filename = str(input).split(".")[-2]
        output = output / Path(filename + ".m4v")
    settings = Settings.query.filter_by(local_id=preset_id).first().settings
    full_settings = ffmpegFullSettings.from_settings(input=input, output=output, settings=settings)
    try:
        worker.queue.put(full_settings)
        logger.debug(f"Adding {str(full_settings)} to queue.")
    except ValueError:
        logger.warning("Tried to dispatch work to empty queue.")

@dispatch_job.route("/dispatch_job", methods=("GET", "POST"))
def dispatch():
    start = Start(meta={"csrf": False})
    start.preset_name.choices = Settings.create_select()
    if start.validate_on_submit():
        try:
            return redirect("/")
        finally:
            dispatch_backend(start.data["preset_name"], start.data["input"], start.data["output"])
    else:
        return render_template("dispatch.html", start=start)

@dispatch_job.route("/bulk_dispatch", methods=("GET", "POST"))
def bulk_dispatch():
    options = Settings.create_select()
    options = "".join([f"<option value={escape(option[0])}>{escape(option[1])}</option>" for option in options])
    options = Markup(options)
        
    if request.method == "GET":
        return render_template("bulk_dispatch.html", options=options)
    else:
        if request.is_json:
            jobs = request.get_json()
            logger.debug(jobs)
            for item in jobs:
                dispatch_backend(item["preset"], Path(item["input"]), Path(item["output"]))
            return "ok", 200
        else:
            return "not ok", 400

