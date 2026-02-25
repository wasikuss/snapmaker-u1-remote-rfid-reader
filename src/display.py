from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

class OLEDDisplay:
    LINE_HEIGHT = 11
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_X_OFFSET = 0
    DISPLAY_Y_OFFSET = 0
    CHAR_WIDTH = 6
    LINE_WIDTH = int(DISPLAY_WIDTH / CHAR_WIDTH)

    def __init__(self, cfg):
        i2c = SoftI2C(
            scl=Pin(cfg["scl"]),
            sda=Pin(cfg["sda"])
        )
        self.oled = SSD1306_I2C(
            self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, i2c
        )

    def clear(self):
        self.oled.fill(0)

    def show(self):
        self.oled.show()

    def text(self, text, line=0, offset_x=0):
        self.oled.text(text, self.DISPLAY_X_OFFSET + offset_x, self.DISPLAY_Y_OFFSET + line * self.LINE_HEIGHT)

    def wrapped_text(self, text, start_line=0, offset_x=0):
        line = start_line

        for paragraph in text.split("\n"):
            while paragraph:
                self.text(paragraph[:self.LINE_WIDTH], line, offset_x=offset_x)
                paragraph = paragraph[self.LINE_WIDTH:]
                line += 1
        
        return line

    def show_message(self, text, start_line=0, clear=True, offset_x=0, wrapped=True):
        if clear:
            self.clear()
        if wrapped:
            next_line = self.wrapped_text(text, start_line=start_line, offset_x=offset_x)
        else:
            self.text(text, line=start_line, offset_x=offset_x)
            next_line = start_line + 1
        self.show()
        return next_line

    def clear_text_bg(self, line):
        self.oled.fill_rect(self.DISPLAY_X_OFFSET, self.DISPLAY_Y_OFFSET + line * self.LINE_HEIGHT, self.DISPLAY_WIDTH, self.LINE_HEIGHT, 0)

    def clear_text_bg_after_text(self, line, text):
        text_width = len(text) * self.CHAR_WIDTH
        self.oled.fill_rect(self.DISPLAY_X_OFFSET + text_width, self.DISPLAY_Y_OFFSET + line * self.LINE_HEIGHT, self.DISPLAY_WIDTH - text_width, self.LINE_HEIGHT, 0)