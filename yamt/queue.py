from typing import Callable, Literal, Union, List
from multiprocessing.queues import Queue
from queue import Empty
from multiprocessing import get_context

def try_(function: Callable, exception: Exception, *args, **kwargs) -> Union[Literal[None], object]:
    try:
        return function(*args, **kwargs)
    except exception:
        pass

class PeekableQueue(Queue):
    def __init__(self, maxsize: int=0) -> None:
        ctx = get_context()
        super().__init__(maxsize=maxsize, ctx=ctx)

    def peek(self) -> List: # TODO: seems kinda too hacky for me
        tab = []
        self._sem.acquire()
        try:
            while not self.empty():
                tab.append(self.get())
            self._sem.release()
        except OSError:
            return []
        for item in tab:
            self.put(item)
        return tab