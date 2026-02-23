import time
import ubinascii
from config import Config
from display import OLEDDisplay
from rfid import RFIDReader
from printer import PrinterClient
from ui_state import UIStateMachine, UIState, UIEvent
from text_scroller import TextScroller
from periodic_timer import PeriodicTimer

cfg = Config()

display = OLEDDisplay(cfg.oled())
rfid = RFIDReader(cfg.rfid())
printer = PrinterClient(cfg.printer())
ui = UIStateMachine(button_pin=9)

rfid_timer = PeriodicTimer(1000)

last_data = None
last_data_text = TextScroller()

channel = 0

IDLE_TEXT = TextScroller("        Hold to change channel. Press to read")

try:
    while True:
        event = ui.handle_event()

        if ui.state == UIState.IDLE:
            next_line = display.show_message(IDLE_TEXT.get_text(display.LINE_WIDTH))
            IDLE_TEXT.scroll()
            if event == UIEvent.LONG_PRESS:
                channel = (channel + 1) % 4
                display.show_message(f"Channel set to {channel}", start_line=next_line, clear=False)
            else:
                display.show_message(f"Channel {channel}", start_line=next_line, clear=False)


        elif ui.state == UIState.READ:
            next_line = display.show_message("Reading..\nHold to send")
            if last_data:
                display.show_message(last_data_text.get_text(display.LINE_WIDTH), start_line=next_line, clear=False)
                last_data_text.scroll()

            if rfid_timer.ready():
                data = rfid.read_text()
                if data is not None and data != last_data:
                    last_data = data
                    last_data_text.set_text(last_data)

            if event == UIEvent.LONG_PRESS and last_data:
                display.show_message("Connecting...")
                data = ubinascii.b2a_base64(last_data).decode("utf-8").strip()
                ok = printer.send_filament_data(channel, data)
                display.show_message("Done" if ok else "Error")
                if ok:
                    last_data = None
                time.sleep(1)

        time.sleep_ms(250)
except Exception as e:
    print("Fatal error:", e)
    display.show_message("FATAL")
