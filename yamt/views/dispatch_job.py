from pathlib import Path
from flask import Blueprint, render_template, redirect, request, jsonify
from jinja2 import Markup, escape
import os
from . import logger
from ..models import Settings
from ..forms.dispatch_job import Start
from ..pyffmpeg import ffmpegFullSettings
from ..forms import path_to_dir_is_valid, path_to_file_is_valid, path_to_new_file_is_valid
from .. import worker

dispatch_job = Blueprint("dispatch_job", __name__, template_folder="templates")

def dispatch_backend(preset_id: int, input: Path, output: Path):
    if path_to_file_is_valid(input):
        if path_to_dir_is_valid(output):
            # input is file, output is directory => output = output / input.filename + ".m4v"
            filename = os.path.basename(input).split(".")
            # movie.avi => [movie, avi]
            # movie.tar.gz.txt.html.what => bad
            if len(filename) != 2:
                return False
            output = output / Path(filename[0] + ".m4v")

        if path_to_new_file_is_valid(output):
            if (settings := Settings.get_by_id(preset_id)):
                full_settings = ffmpegFullSettings(input=input, output=output, settings=settings)
                try:
                    worker.queue.put(full_settings)
                    logger.debug(f"Adding {str(full_settings)} to queue")
                    return True
                except ValueError:
                    logger.warning("Tried to dispatch work to empty queue")
    return False


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
            logger.debug(f"Bulk dispatch: {jobs}")
            items = []
            for i, item in enumerate(jobs):
                if not dispatch_backend(item["preset"], Path(item["input"]), Path(item["output"])):
                    items.append(i)
            if items:
                # TODO: more descriptive errors
                return jsonify({"status": "partial good", "info": items}), 201
            return jsonify({"status": "all good"}), 200
        else:
            return jsonify({"status": "all bad"}), 400

