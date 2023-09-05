from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .bot_base import LineBotMSG
from .bot_messages import create_message
import json

@csrf_exempt
def linebot(request):
    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))

        events = payload.get('events', [])

        for event in events:
            if event['type'] == 'message':
                message_type = event['message']['type']
                reply_token = event['replyToken']
                text = event['message']['text']

                if message_type == 'text':
                    if text.lower() == 'ヘルプ':
                        help_message = "使い方を教えます！オウム返しするだけのbotです！"
                        messages = create_message(help_message)
                    else:
                        messages = create_message(text)

                    line_message = LineBotMSG(messages)
                    line_message.reply(reply_token)

        return JsonResponse({'message': 'OK'}, status=200)
    else:
        return JsonResponse({'message': 'Unsupported method'}, status=405)

