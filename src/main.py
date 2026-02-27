import sys
import time
from config import Config
from display import OLEDDisplay
from event_wrapper import Action, EventWrapper
from rfid import RFIDReader
from printer import PrinterClient
from button_handler import ButtonHandler
from channel_control import ChannelControl, ChannelState

cfg = Config()

display = OLEDDisplay(cfg.oled())
rfid = RFIDReader(cfg.rfid())
printer = PrinterClient(cfg.printer())
btn_config = cfg.button()
btn_1 = ButtonHandler(button_pin=btn_config['pin'])
btn_2 = None
if 'pin2' in btn_config:
    btn_2 = ButtonHandler(button_pin=cfg.button()['pin2'])
event_wrapper = EventWrapper(btn_1, btn_2)

cursor_position = 0

# Initialize channel controls
channels = [ChannelControl(i + 1, display) for i in range(4)]

APP_NAME = "U1 RFID Reader"
MENU_ITEMS = ["CH 1", "CH 2", "CH 3", "CH 4", "Send Data"]

try:
    while True:
        action = event_wrapper.handle_event()

        display.show_message(APP_NAME, start_line=0, clear=False)

        for i, channel in enumerate(channels):
            selected = (cursor_position == i)
            channel.update(selected, action, rfid)
            channel.render(selected)

        send_data_selected = (cursor_position == 4)
        send_data_text = "> Send Data" if send_data_selected else "  Send Data"
        display.clear_text_bg(5)
        display.show_message(send_data_text, start_line=5, clear=False)

        if action == Action.NEXT:
            cursor_position = (cursor_position + 1) % len(MENU_ITEMS)
        elif action == Action.ACTIVATE:
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
