import logging
logger = logging.getLogger("views")

from .dispatch_job import dispatch_job
from .main import main_view
from .settings import settings_view
from .watcher import watch

views = [dispatch_job, main_view, settings_view, watch]