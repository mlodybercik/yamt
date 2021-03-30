import logging
logger = logging.getLogger("views")

import psutil

def get_info():
    return {
    "cpu_usage": psutil.cpu_percent(percpu=True),
    "cpu_avg": [str(round(x / psutil.cpu_count() * 100, 2)) for x in psutil.getloadavg()],
    "v_mem": psutil.virtual_memory(),
    }

from .dispatch_job import dispatch_job
from .main import main_view
from .settings import settings_view
from .watcher import watch

views = [dispatch_job, main_view, settings_view, watch]