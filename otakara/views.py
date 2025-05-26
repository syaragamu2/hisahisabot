import random
import math
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
import json

TIMEOUT_SECONDS = 60  # 1分

def kyory_keisann(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def move_pos(x, y, direction):
    moves = {
        "w": (0, 1), "x": (0, -1),
        "d": (1, 0), "a": (-1, 0),
        "q": (-1, 1), "e": (1, 1),
        "z": (-1, -1), "c": (1, -1)
    }
    return x + moves.get(direction, (0, 0))[0], y + moves.get(direction, (0, 0))[1]

def out_of_bounds(x, y, size):
    return not (0 <= x < size and 0 <= y < size)

def draw_map(player_x, player_y, entities, treasure, size, mode, reveal_all=False):
    """
    entities:
     - 初級、中級なら爆弾リスト
     - 上級ならモンスターリスト
    """
    lines = []
    lines.append(f"【マップ】 (サイズ:{size}x{size}) 難易度:{mode}")
    for y in reversed(range(size)):
        row = ""
        for x in range(size):
            if player_x == x and player_y == y:
                row += "P "
            elif reveal_all:
                if (x, y) == treasure:
                    row += "T "
                elif (x, y) in entities:
                    row += "M " if mode == "c" else "B "
                else:
                    row += ". "
            else:
                row += ". "
        lines.append(row)
    return "\n".join(lines)

@csrf_exempt
def linebot_view(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    body = json.loads(request.body.decode('utf-8'))
    event = body['events'][0]
    user_id = event['source']['userId']
    user_message = event['message']['text'].strip().lower()
    reply_token = event['replyToken']

    cache_key = f'game_state_{user_id}'
    game_state = cache.get(cache_key)
    now = time.time()

    # 新規ゲーム開始コマンド: ゲームスタート a|b|c
    # 例）ゲームスタート a
    if game_state is None:
        if user_message.startswith('ゲームスタート'):
            parts = user_message.split()
            if len(parts) == 2 and parts[1] in ['a', 'b', 'c']:
                mode = parts[1]

                if mode == 'a':  # 初級
                    size = 6
                    treasure = (random.randint(0, size-1), size-1)
                    bombs = []  # 爆弾なし
                    player_x = random.randint(0, size-1)
                    player_y = 0
                    game_state = {
                        'mode': mode,
                        'size': size,
                        'treasure': treasure,
                        'entities': bombs,
                        'player_x': player_x,
                        'player_y': player_y,
                        'move_count': 0,
                        'turn_count': 0,
                        'last_action': now
                    }
                elif mode == 'b':  # 中級
                    size = 6
                    treasure = (random.randint(0, size-1), size-1)
                    bombs = []
                    # 爆弾5個配置（お宝と被らないように）
                    while len(bombs) < 5:
                        bx, by = random.randint(0, size-1), random.randint(1, size-1)
                        if (bx, by) != treasure and (bx, by) not in bombs:
                            bombs.append((bx, by))
                    player_x = random.randint(0, size-1)
                    player_y = 0
                    game_state = {
                        'mode': mode,
                        'size': size,
                        'treasure': treasure,
                        'entities': bombs,
                        'player_x': player_x,
                        'player_y': player_y,
                        'move_count': 0,
                        'turn_count': 0,
                        'last_action': now
                    }
                else:  # 上級 c
                    size = 8
                    treasure = (random.randint(0, size-1), size-1)
                    monsters = []
                    # 最初にモンスター6体のうち3体ランダム配置
                    while len(monsters) < 3:
                        mx, my = random.randint(0, size-1), random.randint(1, size-1)
                        if (mx, my) != treasure and (mx, my) not in monsters:
                            monsters.append((mx, my))
                    player_x = random.randint(0, size-1)
                    player_y = 0
                    game_state = {
                        'mode': mode,
                        'size': size,
                        'treasure': treasure,
                        'entities': monsters,
                        'player_x': player_x,
                        'player_y': player_y,
                        'move_count': 0,
                        'turn_count': 0,
                        'last_action': now,
                        'max_monsters': 6
                    }
                cache.set(cache_key, game_state)
                reply_text = (
                    f"難易度 {mode} のゲームを開始しました！\n"
                    "移動コマンドは w/x/a/d/q/e/z/c です。\n"
                    "w:上, x:下, a:左, d:右, q:左上, e:右上, z:左下, c:右下\n"
                    "お宝は上の段にあります。\n"
                    "「ゲームスタート a」で初級、「ゲームスタート b」で中級、「ゲームスタート c」で上級を開始。\n"
                    "ゲーム開始！どうぞ移動コマンドを送ってください。"
                )
                return JsonResponse(make_reply(reply_token, reply_text))
            else:
                reply_text = "ゲームを開始するには「ゲームスタート a」または「ゲームスタート b」または「ゲームスタート c」と送ってください。"
                return JsonResponse(make_reply(reply_token, reply_text))
        else:
            reply_text = "ゲームが開始されていません。\n「ゲームスタート a」または「ゲームスタート b」または「ゲームスタート c」と送ってください。"
            return JsonResponse(make_reply(reply_token, reply_text))

    # タイムアウト判定
    elapsed = now - game_state.get('last_action', 0)
    if elapsed > TIMEOUT_SECONDS:
        cache.delete(cache_key)
        reply_text = "1分間操作がなかったためゲームを終了しました。\nまた遊びたいときは「ゲームスタート a/b/c」と送ってね！"
        return JsonResponse(make_reply(reply_token, reply_text))

    # 続行時はlast_action更新
    game_state['last_action'] = now

    mode = game_state['mode']
    size = game_state['size']
    treasure = tuple(game_state['treasure'])
    entities = game_state['entities']
    player_x = game_state['player_x']
    player_y = game_state['player_y']
    move_count = game_state['move_count']
    turn_count = game_state['turn_count']

    # プレイヤー移動
    nx, ny = move_pos(player_x, player_y, user_message)
    if out_of_bounds(nx, ny, size):
        reply_text = "※フィールドの外です。移動キャンセル。別のコマンドを送ってください。"
        cache.set(cache_key, game_state)
        return JsonResponse(make_reply(reply_token, reply_text))

    player_x, player_y = nx, ny
    move_count += 1
    turn_count += 1

    # 当たり判定
    if (player_x, player_y) in entities:
        cache.delete(cache_key)
        if mode == 'c':
            reply_text = "💥 モンスターに当たった！ゲームオーバー 💥"
        else:
            reply_text = "💥 爆弾に当たった！ゲームオーバー 💥"
        reply_text += "\n" + draw_map(player_x, player_y, entities, treasure, size, mode, reveal_all=True)
        return JsonResponse(make_reply(reply_token, reply_text))

    # 勝利判定
    if (player_x, player_y) == treasure:
        cache.delete(cache_key)
        reply_text = "🎉 お宝を見つけた！おめでとうございます！ 🎉"
        reply_text += "\n" + draw_map(player_x, player_y, entities, treasure, size, mode, reveal_all=True)
        return JsonResponse(make_reply(reply_token, reply_text))

    # 上級モードのモンスター移動・追加処理
    if mode == 'c':
        # 2ターン毎にモンスター移動
        if turn_count % 2 == 0:
            new_entities = []
            for (mx, my) in entities:
                if random.random() < 0.5:
                    # 移動方向ランダム選択
                    directions = list("wxa" "d" "q" "e" "z" "c")
                    # 斜め含め全8方向ランダム
                    directions = ['w','x','a','d','q','e','z','c']
                    # プレイヤーとの距離最大化（逃げる方向）を試す
                    best_pos = (mx, my)
                    max_dist = kyory_keisann(mx, my, player_x, player_y)
                    random.shuffle(directions)
                    for d in directions:
                        tx, ty = move_pos(mx, my, d)
                        if out_of_bounds(tx, ty, size):
                            continue
                        if (tx, ty) == treasure:
                            continue
                        if (tx, ty) == (player_x, player_y):
                            # モンスターがプレイヤーにぶつかるならゲームオーバーにするため移動OK
                            best_pos = (tx, ty)
                            break
                        if (tx, ty) in entities:
                            continue
                        dist = kyory_keisann(tx, ty, player_x, player_y)
                        if dist > max_dist:
                            max_dist = dist
                            best_pos = (tx, ty)
                    new_entities.append(best_pos)
                else:
                    new_entities.append((mx, my))
            entities = new_entities

        # 10ターン毎に1体追加（最大6体）
        if turn_count % 10 == 0 and len(entities) < game_state.get('max_monsters', 6):
            while True:
                nxm, nym = random.randint(0, size-1), random.randint(1, size-1)
                if (nxm, nym) != treasure and (nxm, nym) not in entities and (nxm, nym) != (player_x, player_y):
                    entities.append((nxm, nym))
                    break

        # モンスターにぶつかった判定（移動後）
        if (player_x, player_y) in entities:
            cache.delete(cache_key)
            reply_text = "💥 モンスターに当たった！ゲームオーバー 💥"
            reply_text += "\n" + draw_map(player_x, player_y, entities, treasure, size, mode, reveal_all=True)
            return JsonResponse(make_reply(reply_token, reply_text))

    # 状態更新
    game_state.update({
        'player_x': player_x,
        'player_y': player_y,
        'entities': entities,
        'move_count': move_count,
        'turn_count': turn_count,
    })
    cache.set(cache_key, game_state)

    # マップ表示
    # 初級のみ距離表示あり
    reply_text = draw_map(player_x, player_y, entities, treasure, size, mode)

    if mode == 'a':
        dist = kyory_keisann(player_x, player_y, treasure[0], treasure[1])
        reply_text += f"\nお宝までの距離：{round(dist, 2)}"

    elif mode == 'b':
        # 爆弾の位置は見えず距離も非表示
        reply_text += "\n爆弾があるので気をつけて！"

    elif mode == 'c':
        reply_text += f"\nモンスター数：{len(entities)}"
        # 距離非表示

    reply_text += "\n移動コマンドを送ってください (w/x/a/d/q/e/z/c)"

    return JsonResponse(make_reply(reply_token, reply_text))


def make_reply(reply_token, text):
    # LINE Messaging API形式の返信データを生成
    return {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
