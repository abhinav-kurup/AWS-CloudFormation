
import json
from channels.generic.websocket import WebsocketConsumer

class SimpleEchoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({"message": "WebSocket connection accepted"}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json.get("message", "")
        self.send(text_data=json.dumps({"echo": msg}))

    def disconnect(self, close_code):
        pass
