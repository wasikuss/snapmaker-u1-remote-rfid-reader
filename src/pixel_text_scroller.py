class PixelTextScroller:
    def __init__(self, text=None, line_width=0, char_width=6):
        self.text = text if text else ""
        self.line_width = line_width + 1
        self.char_width = char_width
        self.min_offset = -len(self.text) * char_width
        self.reset_offset()

    def reset_offset(self):
        self.offset = (self.line_width) * self.char_width

    def set_text(self, text):
        self.text = text
        self.reset_offset()

    def get_text(self):
        return self.text

    def scroll(self, amount=1):
        self.offset -= amount
        if self.offset < self.min_offset:
            self.reset_offset()

    def get_offset(self):
        return self.offset