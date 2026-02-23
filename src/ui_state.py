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
        self._last_change = 0

        self.event = UIEvent.NONE

        # Set up IRQ for the button pin
        self.button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._handle_irq)

    def _handle_irq(self, pin):
        now = time.ticks_ms()
        pressed = pin.value() == 0

        # debounce
        if time.ticks_diff(now, self._last_change) < self.debounce_ms:
            return

        self._last_change = now

        if pressed:
            # button just pressed
            self._pressed_at = now
        else:
            # button released
            if self._pressed_at is not None:
                held = time.ticks_diff(now, self._pressed_at)
                if held >= self.long_press_ms:
                    self.event = UIEvent.LONG_PRESS
                else:
                    self.event = UIEvent.SHORT_PRESS
                self._pressed_at = None

    def handle_event(self):
        if self.event == UIEvent.SHORT_PRESS:
            if self.state == UIState.IDLE:
                self.state = UIState.READ
            elif self.state == UIState.READ:
                self.state = UIState.IDLE

        event = self.event
        self.event = UIEvent.NONE
        return event
