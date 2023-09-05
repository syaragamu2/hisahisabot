def create_message(msg):
    message = [
        {
            'type': 'text',
            'text': msg
        }
    ]
    return message

def create_comic_url(title):
    # ここで漫画のタイトルを元にURLを生成するロジックを実装
    # 例: "One Piece" の場合、該当URLを生成する処理を記述
    comic_url = "https://manga1001.tv/?s=" + title

    # 該当のURLが見つからない場合は None を返す
    return comic_url

def create_carousel(title, comic_url):
    msg = [
        {
            "type": "template",
            "altText": f"{title}の漫画",
            "template": {
                "type": "buttons",
                "imageAspectRatio": "rectangle",
                "imageSize": "cover",
                "title": f"{title}の漫画",
                "text": "詳細を見る",
                "defaultAction": {
                    "type": "uri",
                    "label": "詳細を見る",
                    "uri": comic_url,
                },
            }
        }
    ]
    return msg
