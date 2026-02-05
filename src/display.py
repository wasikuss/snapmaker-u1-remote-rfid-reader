from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

class OLEDDisplay:
    LINE_WIDTH = 9
    LINE_HEIGHT = 10
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_X_OFFSET = 27
    DISPLAY_Y_OFFSET = 26

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

    def text(self, text, line=0):
        self.oled.text(text, self.DISPLAY_X_OFFSET, self.DISPLAY_Y_OFFSET + line * self.LINE_HEIGHT)

    def wrapped_text(self, text, start_line=0):
        line = start_line

        for paragraph in text.split("\n"):
            while paragraph:
                self.text(paragraph[:self.LINE_WIDTH], line)
                paragraph = paragraph[self.LINE_WIDTH:]
                line += 1
        
        return line

    def show_message(self, text, start_line=0, clear=True):
        if clear:
            self.clear()
        next_line = self.wrapped_text(text, start_line=start_line)
        self.show()
        return next_line
