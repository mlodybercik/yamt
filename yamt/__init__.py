from flask import Flask
from os import urandom
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import multiprocessing

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .queue import PeekableQueue

encoding_queue = PeekableQueue()
message_queue = PeekableQueue()

from .pyhandbrake.worker import Worker
from .pyhandbrake import TEST
from .pyhandbrake.folder_scanner import FileWatcher

db = SQLAlchemy()
worker = Worker(encoding_queue, message_queue)
watcher = FileWatcher(encoding_queue, message_queue)

def create_app() -> Flask:
    logger.info("Starting app.")
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = urandom(32).hex()
    Bootstrap(app)

    from .models import Settings
    db.init_app(app)
    @app.cli.command("create_database")
    def create_db():
        db.create_all()
        default = Settings(name="Default", settings=TEST)
        db.session.add(default)
        db.session.commit()
        message_queue.put(1)
        message_queue.put(1)

    from .views import views
    for blueprint in views:
        app.register_blueprint(blueprint)

    from .models import Watchers

    @app.before_first_request # FIXME: i really have to find better alternative to this
    def setup(): 
        logger.debug("Starting all worker threads.")
        worker.start()
        watcher.start()
        Watchers.register_all_watchers(watcher)
    
    return app

def kill_app():
    logger.debug("Killing all helper threads.")
    watcher.observer.stop()
    message_queue.close()
    encoding_queue.close()
