import logging
logger = logging.getLogger(__name__)
from .type_declarations import State
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
from . import better_split

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
    queue = None
    signal = None
    settings = None

    def __init__(self, queue: Queue, signal: Queue):
        self.queue = queue
        self.signal = signal
        logger.debug("Creating handbrake worker thread:")
        super().__init__()

    def run(self):
        signal = None
        logger.info("Handbrake worker started, waiting for inputs:")
        self.state_flag = State.WAITING
        while True:
            while True:
                try:
                    self.settings = try_(self.queue.get, Empty, timeout=1)
                    signal = try_(self.signal.get, Empty, timeout=1)
                except (ValueError, OSError):
                    self.should_exit = True
                    break

                if self.should_exit or self.settings or signal:
                    break
            
            if signal:
                self.handle_signal(signal)
            if self.should_exit:
                break

            assert self.settings != None, "Settings are None???"
            
            running_settings = better_split(str(self.settings))
            self.state_flag = State.WORKING
            logger.info(f"Got work to do: {self.settings}")
            self.process = Popen(running_settings , stdout=PIPE, stderr=PIPE, text=True)

            while self.process.poll() is None:
                # self.process.stdout.readline() is blocking :/
                while (output := self.process.stdout.readline()) and self.process.poll() is None:
                    # rn im using blocking readline to time rest of the loop
                    self.state = self.update_state(output)
                    self.state_raw = output
                    try:
                        signal = try_(self.signal.get, Empty, block=False)
                    except (ValueError, OSError):
                        self.process.kill()
                        self.should_exit = True
                        break
                if self.should_exit:
                    break

            self.state_flag = State.WAITING
            logger.info(f"Work done: {self.settings}")
            logger.info(f"Handbrake exited: {self.process.returncode}")
            self.settings = None
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
                eta = output[13][:-2]
            except (ValueError, IndexError):
                return (percent, 0, 0, 0)
        except (ValueError, IndexError):
            return (0, 0, 0, 0)
        return (percent, curr_fps, avg_fps, eta)


    def handle_signal(self, signal):
        if signal == 1:
            return True
