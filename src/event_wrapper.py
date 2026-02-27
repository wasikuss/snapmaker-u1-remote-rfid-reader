
from button_handler import BtnEvent

class Action:
    NONE = 0
    NEXT = 1
    ACTIVATE = 2

class EventWrapper:
    def __init__(self, btn_1, btn_2=None):
        self.btn1 = btn_1
        self.btn2 = btn_2

    def handle_event(self):
        event_1 = self.btn1.handle_event()
        event_2 = self.btn2.handle_event() if self.btn2 else None

        if self.btn2:
            if event_2 != BtnEvent.NONE:
                return Action.ACTIVATE
            elif event_1 == BtnEvent.NONE:
                return Action.NEXT
        else:
            if event_1 == BtnEvent.LONG_PRESS:
                return Action.ACTIVATE
            elif event_1 == BtnEvent.SHORT_PRESS:
                return Action.NEXT