import pytest
from yamt.models import Settings, Watchers 
from yamt import db
from .test_pyffmpeg import big_settings
from .test_yamt import app

@pytest.fixture(scope="module")
def db_created(app):
    with app.test_client():
        with app.app_context():
            db.create_all()
            yield None

@pytest.fixture(scope="module")
def db_add_settings(db_created, big_settings):
    new_settings = Settings(name="test settings", settings=big_settings)
    db.session.add(new_settings)
    db.session.commit()
    return new_settings

@pytest.fixture(scope="module")
def db_add_watchers(db_created, db_add_settings):
    new_watcher = Watchers(enabled=True, name="test watcher",
                           input="/tmp/input", output="/tmp/output",
                           settings_id=1)

    db.session.add(new_watcher)
    db.session.commit()
    return new_watcher

def test_settings_db(db_created, db_add_settings, big_settings):
    assert len((sett := Settings.query.all())) != 0
    assert sett[0].settings == big_settings
    assert sett[0].name == "test settings"

    assert Settings.create_select() == (1, "test settings")
    assert Settings.get_by_id(1) == big_settings

def test_settings_db(db_created, db_add_watchers, big_settings):
    assert len((watc := Watchers.query.all())) != 0
    assert watc[0].settings_id == 1
    assert watc[0].name == "test watcher"
    assert watc[0].enabled
    assert watc[0].input == "/tmp/input"
    assert watc[0].output == "/tmp/output"
    