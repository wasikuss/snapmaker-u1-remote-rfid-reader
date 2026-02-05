# ui_state.py
import time
from machine import Pin

class UIState:
    IDLE = 0
    READ = 1

class UIEvent:
    NONE = 0
    SHORT_PRESS = 1
    LONG_PRESS = 2

class UIStateMachine:
    def __init__(self, button_pin, long_press_ms=1200, debounce_ms=50):
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.long_press_ms = long_press_ms
        self.debounce_ms = debounce_ms

        self.state = UIState.IDLE

        self._pressed_at = None
        self._long_fired = False
        self._last_change = 0

        self.event = UIEvent.NONE

    def update(self):
        self.event = UIEvent.NONE
        now = time.ticks_ms()
        pressed = self.button.value() == 0

        # debounce
        if time.ticks_diff(now, self._last_change) < self.debounce_ms:
            return

        if pressed and self._pressed_at is None:
            # button just pressed
            self._pressed_at = now
            self._long_fired = False
            self._last_change = now

        elif pressed and self._pressed_at is not None:
            # button held
            if not self._long_fired:
                held = time.ticks_diff(now, self._pressed_at)
                if held >= self.long_press_ms:
                    self.event = UIEvent.LONG_PRESS
                    self._long_fired = True

        elif not pressed and self._pressed_at is not None:
            # button released
            held = time.ticks_diff(now, self._pressed_at)
            if held < self.long_press_ms:
                self.event = UIEvent.SHORT_PRESS
            self._pressed_at = None
            self._last_change = now

    def handle_event(self):
        if self.event == UIEvent.SHORT_PRESS:
            if self.state == UIState.IDLE:
                self.state = UIState.READ
            elif self.state == UIState.READ:
                self.state = UIState.IDLE
