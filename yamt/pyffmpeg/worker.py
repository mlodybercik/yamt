from subprocess import PIPE, Popen, run as sub_run, CalledProcessError
from threading import Thread
from pathlib import Path
from time import time
from typing import List, Literal, Union
from . import better_split, logger
from .ffmpeg_type.type_declarations import Signal, State
from ..queue import PeekableQueue, Empty, try_
from . import ffmpegFullSettings
from .stdqueue import OutWatcher, find_progress
import signal as sys_signal


class Worker(Thread):
    process: Popen = None
    state_flag: State = State.UNKNOWN
    state: dict = None
    should_exit: bool = False
    queue: PeekableQueue = None
    signal: PeekableQueue = None
    settings: ffmpegFullSettings = None
    paused: bool = False
    paused_for: float = 0.0
    paused_at: float = 0.0
    current_task_no: int = 0

    def __init__(self, queue: PeekableQueue, signal: PeekableQueue) -> None:
        self.queue = queue
        self.signal = signal
        logger.debug("Creating worker thread...")
        super().__init__()

    @staticmethod
    def get_video_duration(input: Path) -> Union[float, Literal[-1]]:
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{str(input)}'"
        try:
            output = sub_run(better_split(command), capture_output=True, check=True)
            length = float(output.stdout.decode("ascii")[:-1])
            logger.debug(f"{input} is {length} seconds long")
            return length
        except CalledProcessError:
            logger.warning(f"Couldn't find the length {input}")
            return -1         

    def run(self) -> None:
        logger.debug("Worker spawned")
        self.state_flag = State.WAITING
        while True:
            try:
                message = try_(self.signal.get, Empty, timeout=1)
                settings = try_(self.queue.get, Empty, timeout=1)
            except (ValueError, OSError):
                self.should_exit = True
                break

            if message:
                self.handle_signal(message)

            if settings:
                self.execute_task(settings)
            
            if self.should_exit:
                break
        
        self.state_flag = State.DEAD
        logger.debug("Worker dead")

    def execute_task(self, settings):
        self.settings = settings

        running_settings = better_split(str(self.settings))
        video_duration = self.get_video_duration(self.settings.input)

        self.state_flag = State.WORKING
        start_time = time()

        logger.info(f"Got work to do...")
        logger.debug(f"{self.settings}")
        self.process = Popen(running_settings, stdout=PIPE, stderr=PIPE, text=True)

        err, out = OutWatcher(self.process.stderr, 100), OutWatcher(self.process.stdout, 100)
        err.start()
        out.start()
        logger.debug(f"Created stderr and stdout watchers")

        while self.process.poll() is None:
            # first comes the check for signals.
            # we'll be using blocking queues as loop timer
            try:
                message = try_(self.signal.get, Empty, block=True, timeout=1.0)
            
            except (ValueError, OSError):
                self.process.kill()
                self.should_exit = True
                err.has_to_stop = True
                out.has_to_stop = True
                break
            
            if message:
                self.handle_signal(message)

            with out.lock:
                if (loc := out.buffer.find_and_return_slice(find_progress)):
                    self.state = self.update_state(video_duration, start_time, loc)
            
        err.has_to_stop = True
        out.has_to_stop = True

        err.join()
        out.join()
        logger.debug("Buffer watchers exited")

        self.state_flag = State.WAITING
        logger.info(f"Work done")
        if self.process.returncode:
            logger.warning(f"Subprocess exited: {self.process.returncode}")
        else:
            logger.info(f"Subprocess exited: {self.process.returncode}")

        # cleanup
        self.current_task_no += 1
        self.settings = None
        self.state = None
        self.paused_at = 0
        self.paused_for = 0

    def update_state(self, video_duration: float, time_from_start: float, output: List[str]) -> dict:
        # frame=12                    # int       current frame of an video
        # fps=0.00                    # float     conversion speed
        # stream_0_0_q=0.0            # 
        # bitrate=N/A                 # int       current bitrate
        # total_size=44               # int       current size
        # out_time_us=0               # 
        # out_time_ms=0               # int       current frame, time in ms
        # out_time=00:00:00.000000    # 
        # dup_frames=0                # 
        # drop_frames=0               # 
        # speed=   0x                 # float     conversion speed
        # progress=continue           #           what its doing rn
        if self.paused:
            pausd = time() - self.paused_at
            timed = time() - time_from_start - pausd
        else:
            timed = time() - time_from_start - self.paused_for

        try:
            current_frame = int(output[0][6:])
            fps = float(output[1][4:])
            time_in_s = int(output[6][12:])/1e6
            conversion_speed=output[10][6:]
        except IndexError:
            return None
        
        percent = (time_in_s / video_duration) if video_duration >= 0 else 0
        
        try:
            estimated = round(((1 / percent) * timed) - timed)
            minutes, seconds = divmod(estimated, 60)
            hours, minutes = divmod(minutes, 60)
            estimated = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except (TypeError, ZeroDivisionError):
            estimated = None

        return {"current_frame": current_frame,
                "current_task": self.current_task_no,
                "fps": fps,
                "time_in_s": time_in_s,
                "conversion_speed": conversion_speed,
                "estimated": estimated,
                "percent": __ if (__ := round(percent*100, 2)) >= 0 else 0,
                "paused": self.paused}
            
    def handle_signal(self, signal: Signal) -> None:
        if signal == Signal.STOP:
            logger.info("Skipping current task.")
            self.process.kill()

        elif signal == Signal.QUIT:
            logger.info("Killing worker...")
            if self.process:
                self.process.kill()
                self.should_exit = True
        
        elif signal == Signal.PAUSE:
            if self.process:
                if self.paused:
                    self.process.send_signal(sys_signal.SIGCONT)
                    logger.info("Resuming ffmpeg...")
                    self.paused_for += time() - self.paused_at
                    self.paused = False
                    self.state_flag = State.WORKING
                else:
                    self.process.send_signal(sys_signal.SIGSTOP)
                    logger.info("Pausing ffmpeg...")
                    self.paused_at = time()
                    self.paused = True
                    self.state_flag = State.PAUSED
