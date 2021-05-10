from flask import Flask
from os import urandom
from flask_bootstrap import Bootstrap
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logging.basicConfig(format="%(asctime)s %(name)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

for logger_ in ["pyffmpeg", "views", "observer", "models"]:
    logging.getLogger(logger_).setLevel(logging.INFO)

logger = logging.getLogger(__name__)

from .queue import PeekableQueue

encoding_queue = PeekableQueue()
message_queue = PeekableQueue()

from .pyffmpeg.worker import Worker
from .pyffmpeg.folder_scanner import FileWatcher

db = SQLAlchemy()
worker = Worker(encoding_queue, message_queue)
watcher = FileWatcher(encoding_queue, message_queue)

def create_app(config=None) -> Flask:
    logger.info("Starting app")
    app = Flask(__name__)
    if not config:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else: 
        app.config.update(config)
    app.secret_key = urandom(32).hex()
    Bootstrap(app)

    db.init_app(app)

    @app.cli.command("create_database")
    def create_db():
        db.create_all()

    from .views import views
    for blueprint in views:
        app.register_blueprint(blueprint)

    from .models import Watchers

    @app.before_first_request # FIXME: i really have to find better alternative to this
    def setup():
        if not app.config["TESTING"]:
            from sqlalchemy.exc import OperationalError
            try:
                Watchers.register_all_watchers(watcher)
            except OperationalError:
                logger.warn("Couldn't load watchers, does the database even exist?")
            finally:
                worker.start()
                watcher.start()
                logger.debug("Starting all worker threads")
    
    return app

def kill_app():
    logger.debug("Killing all helper threads")
    watcher.observer.stop()
    message_queue.close()
    encoding_queue.close()

def flash_exception(e: Exception) -> None:
    from jinja2 import Markup, escape
    from traceback import format_exception_only
    formatted_exception = [item.strip() for item in format_exception_only(type(e), e)]

    message = f"""
    <table class="table-sm">
        <tbody>
            {
                "".join([f'<tr><td>{escape(item)}</td></tr>' for item in formatted_exception])
            }
        </tbody>
    </table>
    """
    flash(Markup(message), "error")