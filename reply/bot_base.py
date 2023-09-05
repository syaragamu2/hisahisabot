

import urllib.request
import json
REPLY_ENDPOINT_URL = 'https://api.line.me/v2/bot/message/reply'
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer vBvoZAskncJ4fuLAl44/zRAGFBkH7PARFD4tSo3+KtWNN6x5Y7pgN02cPp+K2J1wWL+mh/zAZXicSJVhaOn0a65lTQ1kPGOCDs0XroOa02HBJ+O3/hlNwuMXJTtQrMj11yY5wWyxWCAb4rlTfy8aUAdB04t89/1O/w1cDnyilFU=', 
}

class LineBotMSG:
    def __init__(self, messages):
        self.messages = messages

    def reply(self, reply_token):
        body = {
            'replyToken': reply_token,
            'messages': self.messages
        }
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        urllib.request.urlopen(req)
