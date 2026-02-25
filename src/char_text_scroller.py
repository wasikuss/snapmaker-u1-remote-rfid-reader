class CharTextScroller:
    def __init__(self, text=None):
        self.pos = 0
        self.text = text or ""

    def set_text(self, text):
        self.text = text
        self.pos = 0

    def get_text(self, max_chars=None):
        text = self.text[self.pos:]
        if max_chars is not None:
            text = text[:max_chars]
        return text
    
    def scroll(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.pos = 0