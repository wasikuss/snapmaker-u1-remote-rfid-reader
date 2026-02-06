from NFC_PN532 import PN532
from machine import Pin, SPI

class RFIDReader:
    BLOCK_SIZE = 4
    READ_BLOCK_COUNT = 4

    def __init__(self, cfg):
        self.start_block = 4
        spi = SPI(baudrate=1000000, polarity=0, phase=0,
                  sck=Pin(cfg["sck"], Pin.OUT),
                  mosi=Pin(cfg["mosi"], Pin.OUT),
                  miso=Pin(cfg["miso"], Pin.IN))
        cs_pin = Pin(cfg["cs"], Pin.OUT)
        rst_pin = Pin(cfg["rst"], Pin.OUT)

        self.rc = PN532(spi, cs_pin, reset=rst_pin, debug=cfg.get("debug", False))
        self.rc.SAM_configuration()
        self.debug = cfg.get("debug", False)

    def detect_card(self):
        uid = self.rc.read_passive_target()
        if not uid:
            if self.debug:
                print("No card detected")
            return None

        if self.debug:
            print("Card detected, UID:", [hex(i) for i in uid])

        return uid

    def read_tlv(self):
        block = self.start_block
        data = bytearray()
        remaining = -1
        remaining_updated = False

        while remaining > 0 or not remaining_updated:
            block_data = self.rc.mifare_classic_read_block(block)
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
