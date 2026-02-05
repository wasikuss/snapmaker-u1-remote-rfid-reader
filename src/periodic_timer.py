import time

class PeriodicTimer:
    def __init__(self, interval_ms):
        self.interval = interval_ms
        self._last = time.ticks_ms()

    def ready(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last) >= self.interval:
            self._last = now
            return True
        return False