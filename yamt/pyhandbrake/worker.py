import logging
from multiprocessing import Value
logger = logging.getLogger(__name__)
from .type_declarations import State
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
import time

def try_(function, exception, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except exception:
        pass

class Worker(Thread):
    process = None
    state_flag = State.UNKNOWN
    state = None
    state_raw = None
    should_exit = False

    def __init__(self, queue: Queue, signal: Queue):
        self.queue = queue
        self.signal = signal
        logger.debug("Creating handbrake worker thread:")
        super().__init__()

    def run(self):
        logger.info("Handbrake worker started, waiting for inputs:")
        self.state_flag = State.WAITING
        while True:
            while True:
                try:
                    settings = try_(self.queue.get, Empty, timeout=1)
                    signal = try_(self.signal.get, Empty, timeout=1)
                except (ValueError, OSError):
                    self.should_exit = True
                    break

                if self.should_exit or settings or signal:
                    break
            
            if signal:
                self.handle_signal(signal)
            if self.should_exit:
                break

            assert settings != None, "Settings are None"
            self.state_flag = State.WORKING
            logger.info(f"Got work to do: {settings}")
            self.process = Popen(settings.split(), stdout=PIPE, stderr=PIPE, text=True)

            while self.process.poll() is None:
                while (output := self.process.stdout.readline()) != "\n" and self.process.poll() is None:
                    self.state = self.update_state(output)
                    self.state_raw = output
                try:
                    signal = try_(self.signal.get, Empty, timeout=1)
                except (ValueError, OSError):
                    self.process.kill()
                    self.should_exit = True
                    break

            self.state_flag = State.WAITING
            logger.info(f"Work done: {settings}")
            self.state = None
            self.state_raw = None

        self.state_flag = State.DEAD
        logger.debug("Worker dead")


    def update_state(self, output):
        # Encoding: task 1 of 1, 82.24 % (11.17 fps, avg 12.36 fps, ETA 00h00m04s)
        #     0       1  2 3  4    5   6    7    8    9   10    11   12     13
        try:
            output = output.split(" ")
            percent = float(output[5])
            try:
                curr_fps = float(output[7][1:])
                avg_fps = float(output[10])
                eta = time.strptime(output[13][:-2], "%Hh%Mm%Ss")
            except (ValueError, IndexError):
                return (percent, 0, 0, 0)
        except (ValueError, IndexError):
            return (0, 0, 0, 0)
        return (percent, curr_fps, avg_fps, eta)


    def handle_signal(self, signal):
        if signal == 1:
            return True
