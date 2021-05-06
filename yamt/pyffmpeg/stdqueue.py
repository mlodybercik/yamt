from threading import Thread, Lock
from io import TextIOWrapper
from typing import Any, Callable, List, Union

class RoundBuffer:
    # deque doesnt work how i want it to
    # also, reusing my old old code
    __slots__ = ["__array__", "__index__", "max_len"]
    def __init__(self, max_len: int) -> None:
        assert max_len > 0, "minsize > 0"
        self.max_len = max_len
        self.__array__ = []
        self.__index__ = 0

    def __replace__(self, index: int, obj: Any):
        self.__array__[index] = obj

    def __getitem__(self, i: int) -> Any:
        return self.__array__[i]

    def append(self, obj: Any) -> None:
        if len(self.__array__) > self.max_len-1:
            self.__replace__(self.__index__ % self.max_len, obj)
            self.__index__ += 1
        else:
            self.__array__.append(obj)
            self.__index__ += 1

    def dump_list(self) -> List[Any]:
        if len(self.__array__) < self.max_len:
            return self.__array__
        else:
            return [self.__array__[x % self.max_len] for x in range(self.__index__, self.__index__ + self.max_len)]

    def find_and_return_slice(self, f: Callable[[Any], bool], length: int = 12) -> Union[List[Any], None]:
        list_ = self.dump_list()
        index = -1
        for i, item in enumerate(list_[::-1]):
            if f(item):
                index = i
                break
        if index + 1:
            start = len(self.__array__) - 1 - index
            end = start + length
            return list_[start:end]
        else:
            return None


class OutWatcher(Thread):
    "Class to watch for stderr/stdout data"
    def __init__(self, pipe: TextIOWrapper, size_of_buffer: int, **kwargs) -> None:
        self.lock = Lock()
        self.has_to_stop = False
        self.pipe = pipe
        self.buffer = RoundBuffer(max_len=size_of_buffer)
        super().__init__(kwargs=kwargs)

    def run(self):
        while not self.has_to_stop:
            if (data := self.pipe.readline()):
                with self.lock:
                    self.buffer.append(data[:-1])

find_progress = lambda obj: True if obj.startswith("frame=") else False