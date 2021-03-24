from flask import Blueprint, render_template, request, flash
from ..forms.create_settings import CreateSettings
from ..pyffmpeg import ffmpegSettings
from ..models import Settings
from .. import db, flash_exception

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
            settings = ffmpegSettings.init_from_unsure(**form_data)
        except Exception as e:
            flash_exception(e)
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
    return str(Settings.get_by_id(id))
