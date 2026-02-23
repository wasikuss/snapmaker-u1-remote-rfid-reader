import socket
import json

class PrinterClient:
    def __init__(self, cfg):
        self.host = cfg["host"]
        self.port = cfg.get("port", 7125)

    def send_filament_data(self, channel, data):
        payload = json.dumps({
            "script": f"FILAMENT_DT_FIXED CHANNEL={channel} DATA='{data}'"
        })

        print("Sending data to printer...", payload)

        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        s = socket.socket()
        s.connect(addr)
        try:
            request = (
                "POST /printer/gcode/script HTTP/1.1\r\n"
                f"Host: {self.host}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(payload)}\r\n\r\n"
                f"{payload}"
            )

            s.send(request.encode())
            s.recv(1024)

            return True
        except Exception as e:
            print("Error sending data to printer:", e)
            return False
        finally:
            s.close()
