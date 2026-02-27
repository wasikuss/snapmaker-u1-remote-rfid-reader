import json

from event_wrapper import Action
from one_shot_timer import OneShotTimer
from periodic_timer import PeriodicTimer
from char_text_scroller import CharTextScroller
from data_validator import DataValidator

class ChannelState:
    EMPTY = 0
    READING = 1
    DATA = 2
    NO_DATA = 3
    BAD_DATA = 4

class ChannelControl:
    def __init__(self, channel_num, display):
        self.channel_num = channel_num
        self.state = ChannelState.EMPTY
        self.last_data = None
        self.display = display
        self.no_data_timer = None
        self.last_data_text = CharTextScroller()
        self.last_data_text_timer = None

    def update(self, selected, action, rfid_reader):
        if selected and action == Action.ACTIVATE:
            if self.state in [ChannelState.NO_DATA, ChannelState.BAD_DATA, ChannelState.EMPTY]:
                self.no_data_timer = None
                self.state = ChannelState.READING
                self.render(selected)
                data, uid = rfid_reader.read_text_and_uid()
                if data is not None:
                    print(f"Data read from channel {self.channel_num}: {data} (UID: {uid})")
                    if DataValidator.validate(data):
                        self.state = ChannelState.DATA
                        self.last_data = {'payload': data, 'uid': uid}
                        self.last_data_text.set_text(self.parse_data_for_display())
                        self.last_data_text_timer = PeriodicTimer(200)
                    else:
                        self.state = ChannelState.BAD_DATA
                        self.last_data = None
                        self.no_data_timer = OneShotTimer(5000)
                else:
                    self.state = ChannelState.NO_DATA
                    self.last_data = None
                    self.no_data_timer = OneShotTimer(5000)
            elif self.state == ChannelState.DATA:
                self.state = ChannelState.EMPTY
                self.last_data = None
                self.last_data_text.set_text("")
                self.last_data_text_timer = None
                self.no_data_timer = None
        
        if self.state in [ChannelState.NO_DATA, ChannelState.BAD_DATA] and self.no_data_timer.ready():
            self.state = ChannelState.EMPTY
            self.no_data_timer = None

    def parse_data_for_display(self):
        try:
            json_data = json.loads(self.last_data['payload'])
            display_parts = []
            if 'brand' in json_data:
                display_parts.append(json_data['brand'])
            if 'type' in json_data:
                display_parts.append(json_data['type'])
            if 'subtype' in json_data:
                display_parts.append(json_data['subtype'])
            if 'color_hex' in json_data:
                display_parts.append(json_data['color_hex'])
            return ' '.join(display_parts)
        except Exception as e:
            print("Error parsing data for display:", e)
            return "Data"
    
    def state_to_text(self):
        if self.state == ChannelState.EMPTY:
            return ""
        elif self.state == ChannelState.READING:
            return "..."
        elif self.state == ChannelState.DATA:
            if self.last_data_text_timer.ready():
                self.last_data_text.scroll()
            return self.last_data_text.get_text(9)  # Show a preview of the data
        elif self.state == ChannelState.NO_DATA:
            return "No data"
        elif self.state == ChannelState.BAD_DATA:
            return "Bad data"

    def render(self, selected):
        prefix = "> " if selected else "  "
        self.display.clear_text_bg(self.channel_num)  # Clear the line explicitly
        self.display.show_message(f"{prefix}CH {self.channel_num} {self.state_to_text()}", start_line=self.channel_num, clear=False, wrapped=False)
