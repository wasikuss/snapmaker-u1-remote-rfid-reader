import socket
import json
import sys

class PrinterClient:
    def __init__(self, cfg):
        self.host = cfg["host"]
        self.port = cfg.get("port", 7125)

    def send_filament_data(self, channel, data):

        json_data = json.loads(data['payload'])
        info = {}
        webhook_payload = {
            'channel': channel,
            'info': info
        }

        if 'brand' in json_data:
            info['VENDOR'] = json_data['brand']

        if 'type' in json_data:
            info['MAIN_TYPE'] = json_data['type']

        if 'subtype' in json_data:
            info['SUB_TYPE'] = json_data['subtype']

        if 'color_hex' in json_data:
            info['RGB_1'] = json_data['color_hex']

        if 'alpha' in json_data:
            info['ALPHA'] = json_data['alpha']

        if 'min_temp' in json_data:
            info['HOTEND_MIN_TEMP'] = json_data['min_temp']

        if 'max_temp' in json_data:
            info['HOTEND_MAX_TEMP'] = json_data['max_temp']

        if 'bed_min_temp' in json_data:
            info['BED_TEMP'] = json_data['bed_min_temp']

        info['CARD_UID'] = data['uid']
        payload = json.dumps(webhook_payload)

        print("Sending data to printer...", payload)

        s = None
        try:
            addr = socket.getaddrinfo(self.host, self.port)[0][-1]
            s = socket.socket()
            s.connect(addr)
            request = (
                "POST /printer/filament_detect/set HTTP/1.1\r\n"
                f"Host: {self.host}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(payload)}\r\n\r\n"
                f"{payload}"
            )

            s.send(request.encode())
            response = s.recv(1024)
            print("Received response:", response)

            return True
        except Exception as e:
            print("Error sending data to printer:", e)
            sys.print_exception(e)
            return False
        finally:
            if s:
                s.close()