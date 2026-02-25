import time

class OneShotTimer:
    def __init__(self, interval_ms):
        self.interval = interval_ms
        self._start = time.ticks_ms()
        self._triggered = False

    def ready(self):
        if self._triggered:
            return False

        now = time.ticks_ms()
        if time.ticks_diff(now, self._start) >= self.interval:
            self._triggered = True
            return True
        return False

    def reset(self):
        self._start = time.ticks_ms()
        self._triggered = False