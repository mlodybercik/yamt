from flask.globals import request
from flask import Blueprint, render_template, flash
from . import logger
from ..forms.create_filewatch import CreateFileWatch
from ..models import Settings, Watchers
from .. import db, watcher

watch = Blueprint("watch", __name__, template_folder="templates")

@watch.route("/add_watcher", methods=["POST", "GET"])
def add_watcher():
    form = CreateFileWatch(meta={"csrf": False})
    form.preset_name.choices = Settings.create_select()
    watchers = Watchers.create_select()
    if form.validate_on_submit():
        new = Watchers.parse_from_form(form.data)
        db.session.add(new)
        db.session.commit()
        flash("Succesfully created new watcher.")
        logger.debug(f"Added {new} to watchers.")
        try:
            watcher.schedule_new(new.local_id, new.input_path, new.output_path, new.settings)
        finally:
            return render_template("watcher.html", form=form, watchers=watchers)
    else:
        return render_template("watcher.html", form=form, watchers=watchers)

@watch.route("/update_watcher", methods=["POST"])
def update_watcher():
    try:
        id = int(request.form["id"])
        checked = True if request.form["checked"] == "true" else False
    except (KeyError, ValueError):
        return "something went wrong", 400

    # 1.     running and checked yes => nothing to do
    # 2.     running and checked no  => enabled=False, unschedule
    # 3. not running and checked no  => nothing to do
    # 4. not running and checked yes => enabled=True, schedule
    if (watcher_query := Watchers.query.filter_by(local_id=id).first()):
        if watcher_query.enabled == checked:
            # 1 and 3
            return "no work to do", 200

        elif watcher_query.enabled and not checked:
            # 2
            if (watcher.check_if_is_running(watcher_query.local_id)):
                watcher.unschedule(watcher_query.local_id)
                watcher_query.enabled = False
                db.session.commit()
                
        elif not watcher_query.enabled and checked:
            # 4
            watcher.schedule_new(watcher_query.local_id, watcher_query.input_path, \
                                 watcher_query.output_path, watcher_query.settings.settings)
            watcher_query.enabled = True
            db.session.commit()

        return "ok", 200

    else:
        return f"no watcher with this id {id}", 400