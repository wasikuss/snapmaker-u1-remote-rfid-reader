import sys
import time
from config import Config
from display import OLEDDisplay
from rfid import RFIDReader
from printer import PrinterClient
from button_handler import ButtonHandler, Event
from pixel_text_scroller import PixelTextScroller
from periodic_timer import PeriodicTimer
from channel_control import ChannelControl, ChannelState

cfg = Config()

display = OLEDDisplay(cfg.oled())
rfid = RFIDReader(cfg.rfid())
printer = PrinterClient(cfg.printer())
btn_handler = ButtonHandler(button_pin=9)

cursor_position = 0

# Initialize channel controls
channels = [ChannelControl(i + 1, display) for i in range(4)]

APP_NAME = "U1 RFID Reader"
MENU_ITEMS = ["CH 1", "CH 2", "CH 3", "CH 4", "Send Data"]

try:
    while True:
        event = btn_handler.handle_event()

        display.show_message(APP_NAME, start_line=0, clear=False)

        for i, channel in enumerate(channels):
            selected = (cursor_position == i)
            channel.update(selected, event, rfid)
            channel.render(selected)

        send_data_selected = (cursor_position == 4)
        send_data_text = "> Send Data" if send_data_selected else "  Send Data"
        display.clear_text_bg(5)
        display.show_message(send_data_text, start_line=5, clear=False)

        if event == Event.SHORT_PRESS:
            cursor_position = (cursor_position + 1) % len(MENU_ITEMS)
        elif event == Event.LONG_PRESS:
            if cursor_position == 4:
                send_data_text = "> Sending "
                display.clear_text_bg(5)
                display.show_message(send_data_text, start_line=5, clear=False)

                for i, channel in enumerate(channels):
                    if channel.state == ChannelState.EMPTY:
                        send_data_text += '.'
                        display.clear_text_bg(5)
                        display.show_message(send_data_text, start_line=5, clear=False)
                    elif channel.state == ChannelState.DATA:
                        send_data_text += 'D'
                        display.clear_text_bg(5)
                        display.show_message(send_data_text, start_line=5, clear=False)

                        ok = printer.send_filament_data(i, channel.last_data)

                        send_data_text = send_data_text[:-1] + ('O' if ok else 'X')
                        display.clear_text_bg(5)
                        display.show_message(send_data_text, start_line=5, clear=False)
                        time.sleep(1)

        time.sleep_ms(30)

except Exception as e:
    print("Fatal error:", e)
    sys.print_exception(e)
    display.show_message("FATAL")
