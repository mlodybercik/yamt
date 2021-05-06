from .observer.watchdog import QueueInotifyObserver, AutomaticDispatcher
from .ffmpeg_type.type_declarations import State
from . import logger

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
        assert type(id) == int
        assert type(input_path) == str
        assert type(output_path) == str

        for value in self._scheduled_tasks.values():
            if value.path == input_path:
                logger.info(f"Tried to create two watchers using same input path {input_path}")
                return False

        logger.info(f"Scheduling new watcher: {id} with settings: {settings}")
        if not self.observer.is_alive:
            self.observer = QueueInotifyObserver(self.signal)
            logger.debug("Observer dead, creating new one...")
            self.start()
            
        watcher = self.observer.schedule(AutomaticDispatcher(output_path, settings, self.task_queue), input_path, False)
        self._scheduled_tasks[id] = watcher
        return True

    def unschedule(self, id):
        if self.observer.is_alive:
            logger.info(f"Unscheduling {id}")
            try:
                del self._scheduled_tasks[id]
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
        
