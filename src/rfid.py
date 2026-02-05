import mfrc522

class RFIDReader:
    BLOCK_SIZE = 4
    READ_BLOCK_COUNT = 4

    def __init__(self, cfg):
        self.start_block = 4
        self.rc = mfrc522.MFRC522(
            cfg["sck"],
            cfg["mosi"],
            cfg["miso"],
            cfg["rst"],
            cfg["cs"]
        )
        self.debug = cfg.get("debug", False)

    def detect_card(self):
        stat, _ = self.rc.request(self.rc.REQIDL)
        if stat != self.rc.OK:
            self.rc.init()
            if self.debug:
                print("No card detected")
            return None
        
        if self.debug:
            print("Card detected")

        stat, uid = self.rc.anticoll()
        if stat != self.rc.OK:
            return None
        
        if self.debug:
            print("Card UID:", [hex(i) for i in uid])

        if self.rc.select_tag(uid) != self.rc.OK:
            return None
        
        if self.debug:
            print("Card selected")

        return uid

    def read_tlv(self):
        block = self.start_block
        data = bytearray()
        remaining = -1
        remaining_updated = False

        while remaining > 0 or not remaining_updated:
            block_data = self.rc.read(block)
            if not block_data:
                if self.debug:
                    print("Failed to read block", block)
                break

            data.extend(block_data)

            if not remaining_updated:
                if len(data) >= 2:
                    remaining = data[1] + 2
                    remaining_updated = True
                    if self.debug:
                        print("TLV length:", remaining)
                else:
                    continue

            remaining -= self.BLOCK_SIZE * self.READ_BLOCK_COUNT
            block += self.READ_BLOCK_COUNT

        if self.debug:
            print("Raw TLV data:", data)

        return data[2:data[1] + 2]
    
    def parse_ndef_text(self, ndef):
        type_len = ndef[1]
        payload_len = ndef[2]
        type = ndef[3:3 + type_len]

        if type == b"T":
            pass
        else:
            if self.debug:
                print("Not a text record", type)
            return None
        
        if self.debug:
            print("NDEF text record detected")

        payload = ndef[3 + type_len:3 + type_len + payload_len]

        status = payload[0]
        encoding = "utf-8" if not (status & 0x80) else "utf-16"
        lang_len = status & 0x3F

        value = payload[1 + lang_len:].decode(encoding)

        if self.debug:
            print("NDEF text value:", value)

        return value
    
    def parse_ndef_mime(self, ndef):
        type_len = ndef[1]
        payload_len = ndef[2]
        type = ndef[3:3 + type_len]
        payload = ndef[3 + type_len:3 + type_len + payload_len]

        if self.debug:
            print("NDEF mime type:", type)

        value = payload.decode("utf-8")

        if self.debug:
            print("NDEF mime payload:", value)

        return value

    def parse_ndef(self, ndef):
        if len(ndef) < 3:
            if self.debug:
                print("Invalid NDEF record", ndef)
            return None
        
        if ndef[0] == 0xD1:
            return self.parse_ndef_text(ndef)
        elif ndef[0] == 0xD2:
            return self.parse_ndef_mime(ndef)
        else:
            if self.debug:
                print("NDEF URI records are not supported")
            return None

    def read_text(self):
        if not self.detect_card():
            return None
        return self.parse_ndef(self.read_tlv())
