from flask.globals import request
from flask import Blueprint, render_template, flash, redirect
from . import logger
from ..forms.create_filewatch import CreateFileWatch
from ..models import Settings, Watchers
from .. import db, watcher

watch = Blueprint("watch", __name__, template_folder="templates")

@watch.route("/add_watcher", methods=["POST", "GET"])
def add_watcher():
    form = CreateFileWatch(meta={"csrf": False})
    form.preset_name.choices = Settings.create_select()

    if form.validate_on_submit():
        # Id is generated after session commit, so rn im commiting new watcher to get new id
        # then im further checking whether watcher for the same path already exists, if yes 
        # im deleting the newly created data.
        if(new := Watchers.parse_from_form(form.data)):
            db.session.add(new)
            db.session.commit()
            if watcher.schedule_new(new.local_id, new.input_path, new.output_path, new.settings):
                logger.debug(f"Added {new} to watchers")

                flash("Succesfully created new watcher.")
                # regenerate all watchers
                watchers = Watchers.create_select()
                return redirect(request.path)
            else:
                db.session.delete(new)
                db.session.commit()
                logger.debug(f"Trying to create watcher for the same input!")
                flash("Watcher for this path already exists!", "warning")
        else:
            flash("Something wrong with the request?", "danger")

    watchers = Watchers.create_select()
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
    # 4. not running and checked yes => enabled=True,  schedule
    if (watcher_query := Watchers.get_by_id(id)):
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

@watch.route("/delete_watcher", methods=["POST"])
def delete_watcher():
    try:
        id = int(request.form["id"])
    except (KeyError, ValueError):
        return "something went wrong", 400
    
    if (watcher_query := Watchers.get_by_id(id)):
        if (watcher.check_if_is_running(id)):
            watcher.unschedule(id)
        db.session.delete(watcher_query)
        db.session.commit()
        return "ok", 200
    return "ok?", 201