from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers.inotify import InotifyEmitter
from watchdog.observers.api import BaseObserver, DEFAULT_OBSERVER_TIMEOUT,\
                                   ObservedWatch
from queue import Empty
from pathlib import Path
from . import logger
from .. import ffmpegFullSettings, is_video
from ..worker import try_

class AutomaticDispatcher(FileSystemEventHandler):
    def __init__(self, output, settings, task_queue):
        self.task_queue = task_queue
        self.output = Path(output)
        self.settings = settings
        super().__init__()

    def on_created(self, event):
        logger.debug(f"Event: {event}")
        if type(event) == FileCreatedEvent:
            path = Path(event.src_path)
            if is_video(event.src_path) and path.is_file():
                output_file = path.name
                if len(output_file.split(".")) >= 2:
                    full_settings = ffmpegFullSettings.from_settings(
                        input=path,
                        output=self.output / output_file,
                        settings=self.settings)
                    
                    try:
                        self.task_queue.put(full_settings)
                    except ValueError:
                        logger.warning("Tried to put work in closed queue.")

class ControlQueueObserver(InotifyEmitter):
        def __init__(self, message_queue, *args, **kwargs):
            self.signal = message_queue
            InotifyEmitter.__init__(self, *args, **kwargs)

        def run(self):
            logger.debug(f"Run started")
            while self.should_keep_running():
                self.queue_events(self.timeout)
                try:
                    signal = try_(self.signal.get, Empty, timeout=1)
                except (ValueError, OSError):
                    self.stop()
                    break
            if not self.should_keep_running():
                logger.debug("watcher dead")

class QueueBaseObserver(BaseObserver):
    def __init__(self, emitter_class, timeout=DEFAULT_OBSERVER_TIMEOUT, **kwargs):
        BaseObserver.__init__(self, emitter_class, timeout)
        self.emitter_kwargs = kwargs
        
    def schedule(self, event_handler, path, recursive):
        with self._lock:
            watch = ObservedWatch(path, recursive)
            self._add_handler_for_watch(event_handler, watch)

            if self._emitter_for_watch.get(watch) is None:
                emitter = self._emitter_class(event_queue=self.event_queue,
                                              watch=watch,
                                              timeout=self.timeout, 
                                              **self.emitter_kwargs)
                self._add_emitter(emitter)
                if self.is_alive():
                    emitter.start()
            self._watches.add(watch)
        return watch

class QueueInotifyObserver(QueueBaseObserver):
    def __init__(self, queue, timeout=DEFAULT_OBSERVER_TIMEOUT):
        logger.debug("Starting filewatcher.")
        QueueBaseObserver.__init__(self, emitter_class=ControlQueueObserver, timeout=timeout, message_queue=queue)
        
