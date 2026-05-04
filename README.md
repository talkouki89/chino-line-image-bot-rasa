# Chino LINE Image Bot Rasa

![GitHub 預覽圖](pic/github.png)

這是一個使用 Python / RasaHQ/rasa / LINE Messaging API 的 LINE 官方帳號機器人專案。功能方向來自 [talkouki89/chino-line-image-bot](https://github.com/talkouki89/chino-line-image-bot)，但入口改成 Rasa custom channel，方便和 Python API、插件與後端服務銜接。

目前專案仍在搬運與調整階段，已先做成 private repo 方便測試效果。

## 主要功能

- LINE Messaging API webhook 接收訊息、postback、成員加入事件。
- Rasa NLU / action server，可保留對話 intent，也能讓插件優先處理明確指令。
- `plugins/` 熱加載，`HOT_RELOAD_PLUGINS=true` 時修改插件後不必重啟整個 Bot。
- 圖搜：SauceNAO、Ascii2D、TraceMoe、Yandex、Iqdb、AnimeTrace、GGJAV。
- 抽圖：Lolicon API 隨機抽圖、R18 抽圖、標籤抽圖，模板按鈕改用 postback。
- 下載：YouTube/yt-dlp、Facebook、Instagram、TikTok、X/Twitter、Pornhub。
- 作品解析：nHentai、紳士漫畫、禁漫天堂、Pixiv。
- 群組工具：歡迎訊息、群組專用發話名稱與頭像、標註查詢、群發。
- 圖片上傳：Freeimage.host API。
- 管理工具：功能開關 Flex 模板、postback 切換、版本/狀態模板。

## 專案結構

```text
.
├─ actions/                         # Rasa custom actions
│  └─ actions.py                    # Rasa help / fallback action
├─ channels/                        # Rasa custom input channel
│  └─ line_official.py              # LINE webhook、postback、歡迎訊息事件入口
├─ chino_rasa/                      # LINE/Rasa bridge 共用模組
│  ├─ context.py                    # 將 LINE event 轉成插件 ctx
│  ├─ help_text.py                  # help 指令集合
│  ├─ line_client.py                # LINE Messaging API client
│  ├─ plugin_runtime.py             # 插件載入與熱加載 runtime
│  ├─ settings.py                   # .env 設定讀取
│  └─ store.py                      # runtime JSON 儲存工具
├─ data/                            # Rasa NLU / rules 訓練資料
│  ├─ nlu.yml                       # intent examples
│  └─ rules.yml                     # rule policy 流程
├─ json/                            # runtime 狀態範例
│  ├─ features.example.json         # 功能開關範例
│  ├─ group_settings.example.json   # 群組歡迎訊息/外觀設定範例
│  └─ state.example.json            # 使用者設定範例
├─ pic/                             # README / GitHub 顯示圖片
│  └─ github.png                    # README 預覽圖
├─ plugins/                         # 所有可熱加載插件
│  ├─ admin_profile_tools.py        # 管理員 MID、聯絡人、群組 ID、speedtest 工具
│  ├─ broadcast.py                  # 管理員群發、預覽、確認、取消
│  ├─ example.py                    # ping/pong 範例插件
│  ├─ facebook_download.py          # fb: Facebook 影片下載
│  ├─ freeimage_upload.py           # #圖片上傳，回覆圖片後上傳 Freeimage.host
│  ├─ group_settings.py             # 群組歡迎訊息、群組專用 Bot 名稱/頭像
│  ├─ help_tools.py                 # 圖搜說明、功能狀態、功能設定、功能切換
│  ├─ image_draw_template.py        # 抽圖 / 標籤抽圖 Flex 模板與 Lolicon API
│  ├─ image_search.py               # 回覆圖片圖搜、模板搜、PicImageSearch 調用
│  ├─ instagram_download.py         # ig: Instagram 圖片 / 影片下載
│  ├─ jmcomic_lookup.py             # c: 禁漫天堂解析
│  ├─ mention_tools.py              # 誰標我 / 清空標註
│  ├─ nhentai.py                    # nHentai 編號解析與 Popular Now
│  ├─ pixiv_lookup.py               # p: Pixiv 作品解析
│  ├─ pornhub_download.py           # ph: Pornhub 影片下載
│  ├─ reply_media_download.py       # 回覆搜 yt/fb/ph/ig
│  ├─ runtime_tools.py              # ren 運行時間模板
│  ├─ tiktok_download.py            # tk: TikTok 圖片 / 影片下載
│  ├─ wnacg.py                      # w: 紳士漫畫解析
│  ├─ x_download.py                 # x:URL / 回覆搜x
│  ├─ ytdlp_download.py             # yt:URL 與 yt-dlp 共用下載工具
│  └─ core/                         # 插件共用工具
│     ├─ cooldown.py                # 抽圖冷卻
│     ├─ features.py                # 功能開關定義與讀寫
│     ├─ freeimage.py               # Freeimage.host API client
│     ├─ gallery_template.py        # 作品解析 Flex 模板
│     ├─ help_template.py           # 說明 / 狀態 / 版本 / 開關 Flex 模板
│     ├─ template.py                # 圖搜結果 Flex 模板
│     ├─ text_convert.py            # 繁簡轉換
│     └─ web_image_search.py        # GGJAV 等網頁圖搜輔助
├─ scripts/                         # Windows 啟動腳本
│  ├─ start_action_server.ps1       # 啟動 Rasa action server
│  ├─ start_cloudflare_tunnel.ps1   # 啟動 Cloudflare Tunnel
│  └─ start_rasa_server.ps1         # 啟動 Rasa server
├─ config.yml                       # Rasa pipeline / policies
├─ credentials.yml                  # LINE custom channel 設定
├─ domain.yml                       # Rasa intents / responses / actions
├─ endpoints.yml                    # Rasa action endpoint
├─ plugin_loader.py                 # 插件載入器
├─ requirements.txt                 # Python 套件
└─ THIRD_PARTY_NOTICES.md           # 第三方項目與法律資訊
```

## 安裝

Rasa 3.6 建議使用 Python 3.10。不要使用 Python 3.14。

### Windows

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

### Linux / macOS

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## 設定

先複製環境變數範例：

Windows：

```powershell
Copy-Item .env.example .env
```

Linux / macOS：

```bash
cp .env.example .env
```

必要設定：

```env
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=
Creator=
ADMIN_USER_IDS=
PUBLIC_BASE_URL=https://你的網域
BOT_TIMEZONE=Asia/Taipei
HOT_RELOAD_PLUGINS=true
```

常用選填：

```env
SauceNAO_api_key=
FREEIMAGE_API_KEY=
PICSEARCH_PROXIES=
PICSEARCH_TIMEOUT=60
YTDLP_COOKIES_FILE=cookies.txt
YTDLP_COOKIES_FROM_BROWSER=
YTDLP_COOKIE=
INSTALOADER_SESSION_USER=
NHENTAI_COOKIE=
DOUYIN_WTF_API_BASE=https://douyin.wtf
```

LINE Developers Webhook URL：

```text
https://你的網域/webhooks/line/webhook
```

`PUBLIC_BASE_URL` 必須是外部可訪問的 HTTPS 網址，圖片、影片等本機暫存媒體會透過：

```text
https://你的網域/webhooks/line/public/media/檔名
```

給 LINE 讀取。

## 啟動

需要兩個終端：一個 action server，一個 Rasa server。

### Windows

終端 1：

```powershell
.\.venv\Scripts\Activate.ps1
rasa run actions
```

終端 2：

```powershell
.\.venv\Scripts\Activate.ps1
rasa run --enable-api --credentials credentials.yml --endpoints endpoints.yml --port 5005
```

也可以使用：

```powershell
.\scripts\start_action_server.ps1
.\scripts\start_rasa_server.ps1
.\scripts\start_cloudflare_tunnel.ps1
```

### Linux / macOS

終端 1：

```bash
source .venv/bin/activate
rasa run actions
```

終端 2：

```bash
source .venv/bin/activate
rasa run --enable-api --credentials credentials.yml --endpoints endpoints.yml --port 5005
```

## Postback 按鈕

功能開關模板與抽圖模板的按鈕已改成 LINE postback：

- 不會在聊天室送出一串指令文字。
- Bot 會在 webhook 內把 postback 轉成內部指令。
- 功能開關使用 `action=toggle_feature&key=<feature_key>`。
- 抽圖模板使用 `cmd=抽圖`、`cmd=r18色圖`、`cmd=tag色圖 標籤`。

## 歡迎訊息

管理員可在群組內設定歡迎訊息：

```text
設定歡迎訊息 歡迎 {UserName} 加入 {GroupName}
查看歡迎訊息
清除歡迎訊息
```

可用變數：

- `{UserName}`：加入成員的 LINE 顯示名稱。
- `{GroupName}`：群組名稱；多人聊天室沒有群組名稱時會使用聊天室 ID 或預設名稱。

設定會寫入 `json/group_settings.json`，該檔案不會提交到 Git。

## 群組專用 Bot 名稱與頭像

LINE Messaging API 支援在每則訊息上指定 sender 的 `name` 與 `iconUrl`。這會改變訊息泡泡上的顯示名稱與頭像，不會改變官方帳號本身名稱，也不會改變聊天室列表或官方帳號資料頁。

管理員可在群組內設定：

```text
設定機器人名稱 智乃圖搜
設定機器人頭像 https://example.com/avatar.png
查看機器人外觀
清除機器人外觀
```

注意：頭像網址必須是 LINE 可讀取的 HTTPS 圖片 URL。

## 常用指令

```text
圖搜說明
功能狀態
功能設定
功能切換 <key>

回覆搜圖 / 回覆搜1 / 回覆搜2 / 回覆搜3 / 回覆搜4 / 回覆搜5 / 回覆搜6 / 回覆搜7
模板搜 / 模板搜1 / 模板搜2 / 模板搜3
#1 / #2 / #3

抽圖模板
抽圖 / 色圖 / 抽圖無AI / r18色圖 / R18無AI
tag色圖 女僕

yt:https://...
fb:https://...
ig:https://...
tk:https://...
x:https://...
ph:https://...

n:123456 / n:popular
w:123456
c:123456
p:123456

#圖片上傳
誰標我 / 清空標註
ren
ping
```

## PicImageSearch

`requirements.txt` 已使用：

```text
PicImageSearch @ git+https://github.com/kitUIN/PicImageSearch.git
```

可調整：

- `SauceNAO_api_key`：SauceNAO API key。
- `PICSEARCH_PROXIES`：代理，例如 `http://127.0.0.1:7890`。
- `PICSEARCH_TIMEOUT`：圖搜 timeout 秒數。
- `PICSEARCH_VERIFY_SSL`：是否驗證 SSL。
- `ASCII2D_BASE_URLS`：Ascii2D base URL。
- `YANDEX_BASE_URLS`：Yandex base URL。

## 第三方項目

本專案使用或相容下列第三方項目，請同時遵守各自授權與使用規範：

- [Rasa](https://github.com/RasaHQ/rasa)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [PicImageSearch](https://github.com/kitUIN/PicImageSearch)
- [Lolicon API](https://docs.api.lolicon.app/)
- [jmcomic](https://github.com/hect0x7/JMComic-Crawler-Python)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [douyin.wtf](https://douyin.wtf/)
- [Freeimage.host API](https://freeimage.host/page/api)
- [Instaloader](https://github.com/instaloader/instaloader)

更多法律與注意事項請看 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 驗證

```bash
python -m compileall actions channels chino_rasa plugins plugin_loader.py
rasa data validate
rasa train
```

如果 `rasa` 指令不可用，請先啟用 Python 3.10 的 `.venv`。
