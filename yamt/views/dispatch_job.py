import logging
logger = logging.getLogger(__name__)
from flask import Blueprint, render_template, redirect
from ..models import Settings
from ..forms.dispatch_job import Start
from ..pyhandbrake import HandbrakeFullSettings
from .. import worker

dispatch_job = Blueprint("dispatch_job", __name__, template_folder="templates")

@dispatch_job.route("/dispatch_job", methods=("GET", "POST"))
def dispatch():
    start = Start(meta={"csrf": False})
    start.preset_name.choices = Settings.create_select()
    if start.validate_on_submit():
        settings = Settings.query.filter_by(local_id=start.data["preset_name"]).first().settings
        full_settings = HandbrakeFullSettings.from_settings(input=start.data["input"], output=start.data["output"], settings=settings)
        try:
            return redirect("/")
        finally:
            try:
                worker.queue.put(full_settings)
                logger.debug(f"Adding {str(full_settings)} to queue.")
            except ValueError:
                logger.warning("Tried to dispatch work to empty queue.")
    else:
        return render_template("dispatch.html", start=start)