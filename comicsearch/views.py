from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .bot_base import LineBotMSG
from .bot_comics import create_message,create_carousel,create_comic_url
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
                    if text.lower() == 'ヘルプ' or "へるぷ" or "help":
                        help_message = "使い方\n読みたい漫画の名前をメッセージに送ってひさ。その漫画を見れるリンクを送るヒサ！漫画のタイトルに含まれている単語をなるべく短く送ってくれると引っ掛かりやすいひさ。"
                        messages = create_message(help_message)
                    else:
                        title = text
                        # 漫画のURLを取得
                        comic_url = create_comic_url(title)
                        #if comic_url:
                            # カルーセルメッセージを作成
                        messages = create_message(comic_url)
                        #else:
                        #    # 該当する漫画が見つからない場合のメッセージ
                        #    messages = create_message(f"「{title}」の漫画は見つかりませんでした。")

                    line_message = LineBotMSG(messages)
                    line_message.reply(reply_token)

        return JsonResponse({'message': 'OK'}, status=200)
    else:
        return JsonResponse({'message': 'Unsupported method'}, status=405)

