FEATURE_KEY = "image_draw_template"

import threading
from urllib.parse import urlencode

import requests

from plugins.core.cooldown import check_draw_cooldown
from plugins.core.text_convert import to_simplified, to_traditional


LOLICON_API_URL = "https://api.lolicon.app/setu/v2"
LOLICON_API_DOCS_URL = "https://docs.api.lolicon.app/"
RANDOM_IMAGE_COMMANDS = {
    "__draw_random": (0, False),
    "__draw_random_no_ai": (0, True),
    "__draw_r18": (1, False),
    "__draw_r18_no_ai": (1, True),
    "色圖": (0, False),
    "一般抽圖": (0, False),
    "抽圖無ai": (0, True),
    "抽圖無AI": (0, True),
    "無ai抽圖": (0, True),
    "無AI抽圖": (0, True),
    "抽圖r18": (1, False),
    "r18色圖": (1, False),
    "R18色圖": (1, False),
    "色圖r18": (1, False),
    "r18無ai": (1, True),
    "R18無AI": (1, True),
    "無ai r18": (1, True),
}
TAG_IMAGE_PREFIXES = ("tag色圖", "色圖tag", "標籤抽圖")

GAME_TAGS = [
    ("Nikke", "Nikke"),
    ("原神", "原神"),
    ("崩壞", "崩壞"),
    ("蔚藍檔案", "ブルーアーカイブ"),
    ("賽馬娘", "ウマ娘"),
    ("明日方舟", "アークナイツ"),
    ("FGO", "fgo"),
    ("公主連結", "プリンセスコネクト"),
    ("碧藍航線", "アズールレーン"),
    ("艦隊收藏", "艦隊これくしょん"),
    ("Shadowverse", "Shadowverse"),
]

OTHER_TAGS = [
    ("VTB", "vtb"),
    ("女僕", "メイド"),
    ("泳裝", "水着"),
    ("制服", "制服"),
    ("貓耳", "猫耳"),
    ("白髮", "白髪"),
    ("黑髮", "黒髪"),
    ("金髮", "金髪"),
    ("長髮", "長髪"),
    ("短髮", "短髪"),
]

CHARACTER_TAGS = [
    ("初音未來", "初音ミク"),
    ("雷電將軍", "雷電将軍"),
    ("胡桃", "胡桃"),
    ("甘雨", "甘雨"),
    ("砂狼白子", "砂狼シロコ"),
    ("小鳥遊星野", "小鳥遊ホシノ"),
    ("愛麗絲", "アリス"),
    ("阿米婭", "アーミヤ"),
]


def handle(ctx):
    command = ctx.cmd.strip()
    if command in {"抽圖", "抽圖模板", "抽圖說明", "抽圖功能"}:
        ctx.send_template(ctx.to, build_draw_template())
        return True
    if command in RANDOM_IMAGE_COMMANDS:
        if not check_lolicon_cooldown(ctx):
            return True
        r18, exclude_ai = RANDOM_IMAGE_COMMANDS[command]
        return handle_random_lolicon(ctx, r18=r18, exclude_ai=exclude_ai)
    if command.startswith(TAG_IMAGE_PREFIXES):
        return handle_lolicon_tags(ctx)
    return False


def check_lolicon_cooldown(ctx):
    if getattr(ctx, "is_admin", False):
        return True
    allowed, remaining = check_draw_cooldown(ctx.sender)
    if not allowed:
        ctx.reply(f"抽圖冷卻中，請 {remaining} 秒後再試。")
        return False
    return True


def handle_random_lolicon(ctx, r18=0, exclude_ai=False):
    threading.Thread(
        target=send_random_lolicon_async,
        args=(ctx, r18, exclude_ai),
        daemon=True,
    ).start()
    return True


def send_random_lolicon_async(ctx, r18=0, exclude_ai=False):
    try:
        data = request_lolicon({"r18": r18, "excludeAI": exclude_ai})
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply("隨機色圖讀取失敗。")
        return

    label = "R18 隨機色圖" if r18 else "一般隨機色圖"
    if exclude_ai:
        label += "（無 AI）"
    send_lolicon_result(ctx, data, label=label)


def handle_lolicon_tags(ctx):
    tags = extract_tag_query(ctx.text)
    if not tags:
        ctx.reply("請輸入標籤，範例：tag色圖 女僕")
        return True
    if not check_lolicon_cooldown(ctx):
        return True
    query_tags = [to_simplified(tag) for tag in tags.split()]
    display_tags = " ".join(to_traditional(tag) for tag in query_tags)
    try:
        data = request_lolicon({"tag": [[tag] for tag in query_tags], "r18": 1})
    except Exception as exc:
        ctx.log_error(exc)
        ctx.reply("tag 色圖讀取失敗。")
        return True

    send_lolicon_result(ctx, data, label=f"Tag 色圖：{display_tags}")
    return True


def extract_tag_query(text):
    for prefix in TAG_IMAGE_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            return text[len(prefix):].strip()
    return ""


def request_lolicon(extra_payload):
    payload = {
        "num": 1,
        "size": ["regular", "original"],
        "excludeAI": False,
    }
    payload.update(extra_payload)
    response = requests.post(
        LOLICON_API_URL,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data


def send_lolicon_result(ctx, data, label):
    if not data.get("data"):
        ctx.reply("找不到圖片，請換個標籤或稍後再試。")
        return
    item = data["data"][0]
    urls = item.get("urls") or {}
    image_url = urls.get("regular") or urls.get("original")
    text = (
        str(label) +
        f"\n\n標題：{item.get('title')}"
        f"\n作者：{item.get('author')}"
        f"\nR18：{format_bool_flag(item.get('r18'))}"
        f"\nAI：{format_ai_flag(item.get('aiType'))}"
        f"\nPixiv：https://www.pixiv.net/artworks/{item.get('pid')}"
    )
    ctx.cl.relatedMessage(ctx.to, text, ctx.msg_id)
    if not image_url:
        ctx.reply("找不到圖片 URL。")
        return
    try:
        ctx.cl.sendImageWithURL(ctx.to, image_url)
    except Exception as exc:
        ctx.log_error(exc)


def format_ai_flag(ai_type):
    try:
        return "否" if int(ai_type or 0) == 0 else "是"
    except (TypeError, ValueError):
        return "否" if not ai_type else "是"


def format_bool_flag(value):
    if isinstance(value, str):
        return "是" if value.strip().lower() in ("1", "true", "yes", "on") else "否"
    return "是" if bool(value) else "否"


def build_draw_template():
    return {
        "type": "flex",
        "altText": "抽圖功能",
        "contents": {
            "type": "carousel",
            "contents": [
                random_draw_bubble(),
                tag_bubble("作品標籤", GAME_TAGS),
                tag_bubble("常用標籤", OTHER_TAGS),
                tag_bubble("角色標籤", CHARACTER_TAGS),
            ],
        },
    }


def random_draw_bubble():
    return bubble(
        [
            title("抽圖"),
            note("按鈕會送出 postback，Bot 會直接執行，不會在聊天室送出指令文字。"),
            separator(),
            note("一般：抽圖"),
            note("一般無 AI：抽圖無AI"),
            note("R18：r18色圖"),
            note("R18 無 AI：R18無AI"),
            separator(),
            note("標籤抽圖：tag色圖 標籤"),
        ],
        [
            button("抽圖", "__draw_random"),
            button("抽圖無 AI", "__draw_random_no_ai"),
            button("R18 色圖", "__draw_r18"),
            button("R18 無 AI", "__draw_r18_no_ai"),
            button("Tag 色圖", "tag色圖"),
            url_button("Lolicon API", LOLICON_API_DOCS_URL),
        ],
    )


def tag_bubble(title_text, tags):
    contents = [
        title(title_text),
        note("按下標籤後會用 tag色圖 進行搜尋。"),
        note("如果查不到，可改用日文、英文或簡體標籤再試。"),
        separator(),
    ]
    return bubble(contents, [tag_button(label, tag) for label, tag in tags])


def bubble(body_contents, footer_contents):
    return {
        "type": "bubble",
        "styles": {
            "body": {"backgroundColor": "#fff7fb"},
            "footer": {"backgroundColor": "#fff7fb"},
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#fff7fb",
            "contents": body_contents,
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": button_rows(footer_contents),
        },
    }


def title(text):
    return {"type": "text", "text": text, "weight": "bold", "size": "xl", "color": "#5b3b73", "wrap": True}


def note(text):
    return {"type": "text", "text": text, "size": "sm", "color": "#555555", "wrap": True}


def separator():
    return {"type": "separator", "margin": "md", "color": "#f6c6d9"}


def tag_button(label, tag):
    return button(label, f"tag色圖 {tag}")


def button_rows(buttons, columns=2):
    rows = []
    for index in range(0, len(buttons), columns):
        row_buttons = buttons[index:index + columns]
        while len(row_buttons) < columns:
            row_buttons.append({"type": "box", "layout": "vertical", "contents": [], "flex": 1})
        rows.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": row_buttons,
        })
    return rows


def button(label, command):
    return {
        "type": "button",
        "style": "primary",
        "height": "sm",
        "color": "#f08ab8",
        "action": {
            "type": "postback",
            "label": label,
            "data": urlencode({"cmd": command}),
        },
    }


def url_button(label, url):
    return {
        "type": "button",
        "style": "secondary",
        "height": "sm",
        "color": "#f08ab8",
        "action": {
            "type": "uri",
            "label": label,
            "uri": url,
        },
    }
