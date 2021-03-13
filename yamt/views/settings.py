from flask import Blueprint, render_template, request, flash
from traceback import format_exception
from ..forms.create_settings import CreateSettings
from ..pyhandbrake.type_declarations import SETTINGS
from ..pyhandbrake import HandbrakeSettings
from ..models import Settings
from .. import db

settings_view = Blueprint("settings", __name__, template_folder="templates")

@settings_view.route("/add_settings", methods=["GET", "POST"])
def add_settings():
    form = CreateSettings(meta={"csrf": False})
    if form.validate_on_submit():
        form_data = {}
        try:
            for key, value in form.data.items():
                if not value:
                    continue
                form_data[key] = value
            name = form_data["preset_name"]
            form_data = {x:form_data[x] for x in form_data if x in SETTINGS}
            settings = HandbrakeSettings(**form_data)
        except Exception as e:
            flash(f"{format_exception(type(e), e, e.__traceback__)}", "error")
            return render_template("settings.html", form=form)
        new_settings = Settings(name=name, settings=settings)
        db.session.add(new_settings)
        db.session.commit()

        flash("Succesfully added new preset.")
        return render_template("settings.html", form=form)

    else:
        return render_template("settings.html", form=form)

@settings_view.route("/render_settings", methods=["POST", "GET"])
def render_settings():
    try:
        id = int(request.form["id"])
    except (ValueError, KeyError):
        return ""
    return str(Settings.query.filter_by(local_id=id).first().settings)
