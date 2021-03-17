import logging
logger = logging.getLogger(__name__)
from .observer.watchdog import QueueInotifyObserver, AutomaticDispatcher
from .type_declarations import State


class FileWatcher:
    _scheduled_tasks = {}
    def __init__(self, queue, signal):
        self.signal = signal
        self.task_queue = queue
        logger.debug("Creating inotify observer")
        self.observer = QueueInotifyObserver(signal)

    start    = lambda self: self.observer.start()
    is_alive = lambda self: self.observer.is_alive()

    def check_if_is_running(self, id):
        try:
            return id in self._scheduled_tasks
        except KeyError:
            return False

    def schedule_new(self, id, input_path, output_path, settings):
        assert type(input_path) == str
        assert type(output_path) == str
        logger.info(f"Scheduling new watcher: {id} with settings: {settings}")
        if self.observer.is_alive:
            watcher = self.observer.schedule(AutomaticDispatcher(output_path, settings, self.task_queue), input_path, False)
            self._scheduled_tasks[id] = watcher
        else:
            logger.debug("Observer dead, creating new one:")
            self.observer = QueueInotifyObserver(self.signal)
            self.start()
            watcher = self.observer.schedule(AutomaticDispatcher(output_path, settings, self.task_queue), input_path, False)

    def unschedule(self, id):
        if self.observer.is_alive:
            logger.info(f"Unscheduling {id}")
            try:
                self.observer.unschedule(self._scheduled_tasks[id])
            except KeyError:
                return False
            return True

    @property
    def state_flag(self):
        if not self.is_alive():
            return State.DEAD
        else:
            return State.WORKING
        
