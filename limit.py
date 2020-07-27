import time
import collections
import threading


class Limiter(object):
    def __init__(self, max=1, period=1.0):
        self.max = max
        self.period = period
        self._calls = collections.deque()
        self._lock = threading.Lock()
        
    @property
    def _timespan(self):
        return self._calls[-1] - self._calls[0]

    def __enter__(self):
        with self._lock:
            if len(self._calls) >= self.max:
                until = time.time() + self.period - self._timespan
                sleeptime = until - time.time()
                if sleeptime > 0:
                    time.sleep(sleeptime)
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            self._calls.append(time.time())
            while self._timespan >= self.period:
                self._calls.popleft()
