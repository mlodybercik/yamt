from os import stat
from sqlalchemy.orm import relationship
from . import db

class Settings(db.Model):
    __tablename__ = "settings"
    local_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    settings = db.Column(db.PickleType())
    watchers_id = db.Column(db.Integer, db.ForeignKey("watchers.local_id"))

    def __repr__(self):
        return f"<id={self.local_id} name={self.name} pickle={self.settings}>"

    @staticmethod
    def create_select():
        presets = []
        for entry in Settings.query.all():
            presets.append((entry.local_id, entry.name))
        return presets

class Watchers(db.Model):
    __tablename__ = "watchers"
    settings_id = db.Column(db.Integer, db.ForeignKey("settings.local_id"), nullable=False)
    settings = db.relationship(Settings, foreign_keys=settings_id, backref="watchers")

    local_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enabled = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(32))
    input_path = db.Column(db.String(32))
    output_path = db.Column(db.String(32))

    def __repr__(self):
        return f"<id={self.local_id} name={self.name} input={self.input_path}, output={self.output_path}>"

    @staticmethod
    def parse_from_form(form):
        return Watchers(settings_id=form["preset_name"], name=form["name"], \
                        input_path=str(form["input_path"]), output_path=str(form["output_path"]))

    @staticmethod
    def create_select():
        presets = {}
        for entry in Watchers.query.all():
            presets[entry.local_id] = (entry.name, entry.settings.name, \
                                       entry.input_path, entry.output_path, \
                                       entry.enabled)
        return presets

    @staticmethod
    def register_all_watchers(watcher):
        for entry in Watchers.query.all():
            if entry.enabled:
                watcher.schedule_new(entry.local_id, entry.input_path, entry.output_path, entry.settings.settings)
    