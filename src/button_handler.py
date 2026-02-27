import time
from machine import Pin

class BtnEvent:
    NONE = 0
    SHORT_PRESS = 1
    LONG_PRESS = 2

class ButtonHandler:
    def __init__(self, button_pin, long_press_ms=1000, debounce_ms=100):
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.long_press_ms = long_press_ms
        self.debounce_ms = debounce_ms

        self._pressed_at = None
        self._last_change = 0

        self.event = BtnEvent.NONE

        self.button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._handle_irq)

    def _handle_irq(self, pin):
        now = time.ticks_ms()
        pressed = pin.value() == 0

        # debounce
        if time.ticks_diff(now, self._last_change) < self.debounce_ms:
            return
        
        self._last_change = now

        if pressed:
            self._pressed_at = now
        else:
            if self._pressed_at is not None:
                held = time.ticks_diff(now, self._pressed_at)
                if held >= self.long_press_ms:
                    self.event = BtnEvent.LONG_PRESS
                else:
                    self.event = BtnEvent.SHORT_PRESS
                self._pressed_at = None

    def handle_event(self):
        event = self.event
        self.event = BtnEvent.NONE
        return event
