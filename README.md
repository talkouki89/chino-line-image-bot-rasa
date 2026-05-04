# Chino LINE Image Bot Rasa

這是一個 Python / Rasa 版 LINE Bot，目標是把 [`talkouki89/chino-line-image-bot`](https://github.com/talkouki89/chino-line-image-bot) 中可搬運的外掛功能搬到 LINE 官方 Messaging API 架構。Bot 會先用熱載入外掛處理原本的文字指令，外掛沒有命中時再交給 Rasa NLU / actions。

## 風險提醒

本專案使用 LINE 官方 Messaging API，不使用 LINE 個人帳號登入，也不使用非官方收訊輪詢。這能降低個人帳號自動化的風控風險，但官方 API 能力與原專案不同，不能完全 1:1 還原所有帳號行為。

請注意：

- 官方 API 傳送圖片/影片需要公開 HTTPS URL，因此下載後的本機媒體需要透過 `PUBLIC_BASE_URL` 暫時公開。
- 回覆圖片搜尋需要 LINE webhook event 提供可下載的 message id；不同聊天室或回覆型態可能受官方 API 限制。

## 主要功能

- LINE 官方 Messaging API webhook 收訊與回覆。
- RasaHQ/rasa NLU / action server，可接 Python API 與後續對話流程。
- 熱載入 `plugins/*.py`，修改外掛後下一次訊息自動重載，不需要重啟 Rasa。
- 圖片反搜：SauceNAO、Ascii2D、TraceMoe、AnimeTrace、Yandex、Iqdb、GGJAV。
- 抽圖功能使用 Lolicon API，支援隨機圖、R18、標籤圖與排除 AI 圖。
- X/Twitter、YouTube、Facebook、Pornhub、Instagram、TikTok 下載相關指令。
- nHentai、紳士漫畫、禁漫天堂、Pixiv 編號解析模板。
- Freeimage.host 圖床上傳。
- 誰標我 / 清空標註、運行時間模板、功能開關與使用次數資料。

## 專案結構

```text
.
├── actions/                 # Rasa custom actions
├── channels/
│   └── line_official.py     # LINE 官方 Messaging API custom channel
├── chino_rasa/              # LINE 相容層、設定、狀態儲存
├── data/                    # Rasa NLU / rules
├── json/                    # runtime 狀態範例與執行時資料
├── plugins/                 # 熱載入外掛與輔助模組
│   ├── admin_profile_tools.py
│   ├── broadcast.py
│   ├── example.py           # 熱載入外掛範例
│   ├── facebook_download.py
│   ├── freeimage_upload.py
│   ├── image_draw_template.py
│   ├── image_search.py
│   ├── instagram_download.py
│   ├── jmcomic_lookup.py
│   ├── mention_tools.py
│   ├── nhentai.py
│   ├── pixiv_lookup.py
│   ├── pornhub_download.py
│   ├── reply_media_download.py
│   ├── runtime_tools.py
│   ├── tiktok_download.py
│   ├── wnacg.py
│   ├── x_download.py
│   ├── ytdlp_download.py
│   └── core/                # cooldown / features / Flex template / Freeimage / 繁簡轉換
├── tag/                     # mention_tools 使用的標註資料
├── config.yml               # Rasa pipeline / policies
├── credentials.yml          # LINE custom channel 設定
├── domain.yml               # Rasa intents / responses / actions
├── endpoints.yml            # Rasa action endpoint
├── plugin_loader.py         # 外掛熱載入管理器
└── THIRD_PARTY_NOTICES.md   # 第三方授權資訊
```

## 安裝

Rasa 3.6 需要 Python 3.10。若系統預設是 Python 3.14，請另外安裝 Python 3.10 並建立虛擬環境。

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

本專案主要使用：

- [Rasa](https://github.com/RasaHQ/rasa)
- [PicImageSearch](https://github.com/kitUIN/PicImageSearch)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [instaloader](https://github.com/instaloader/instaloader)

## 設定

複製 `.env.example` 成 `.env`，再填入 LINE 官方 API 與需要的 API key。

Windows：

```powershell
Copy-Item .env.example .env
```

Linux / macOS：

```bash
cp .env.example .env
```

最少需要填：

```env
# LINE Developers > Messaging API > Channel access token
LINE_CHANNEL_ACCESS_TOKEN=

# LINE Developers > Basic settings > Channel secret
LINE_CHANNEL_SECRET=

# Bot 作者 / 最高管理員的 LINE userId
Creator=

# 對外公開 HTTPS 網址，不含結尾斜線
PUBLIC_BASE_URL=

# 預設台灣時間
BOT_TIMEZONE=Asia/Taipei

# 啟用外掛熱載入
HOT_RELOAD_PLUGINS=true
```

常用選填項目：

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

### LINE Developers

Webhook URL 設定：

```text
https://你的網域/webhooks/line/webhook
```

本機測試可以使用 ngrok 或 Cloudflare Tunnel，把公開 HTTPS 網址填進 `PUBLIC_BASE_URL`。本機下載後要傳回 LINE 的媒體，會從下列路徑暫時公開：

```text
https://你的網域/webhooks/line/public/media/檔名
```

### Runtime JSON

`json/features.json`、`json/state.json`、`json/recent_messages.json`、`json/group_ids.json` 是機器運行時資料，已被 `.gitignore` 排除，不建議提交真實 userId、群組 ID、使用次數或個人狀態。

格式可以參考：

- `json/features.example.json`
- `json/state.example.json`

第一次啟動時，如果正式檔案不存在，程式會依預設值建立。需要手動建立時可以複製範例：

Windows：

```powershell
Copy-Item json\features.example.json json\features.json
Copy-Item json\state.example.json json\state.json
```

Linux / macOS：

```bash
cp json/features.example.json json/features.json
cp json/state.example.json json/state.json
```

`tag/*.json` 是使用者標註紀錄，也已被 `.gitignore` 排除；`tag/.gitkeep` 只用來保留空資料夾。

## PicImageSearch 說明

`requirements.txt` 已加入：

```text
PicImageSearch @ git+https://github.com/kitUIN/PicImageSearch.git
```

本專案目前沿用同步 PicImageSearch 寫法，但圖搜外掛會在背景 thread 執行，避免搜尋期間阻塞其他訊息。

相關設定：

- `SauceNAO_api_key`：SauceNAO API key，使用 `回覆搜1` / `模板搜1` / `#1` 建議填。
- `PICSEARCH_PROXIES`：PicImageSearch proxy，例如 `http://127.0.0.1:7890`。
- `PICSEARCH_TIMEOUT`：搜尋 timeout 秒數。
- `PICSEARCH_VERIFY_SSL`：是否驗證 SSL。
- `ASCII2D_BASE_URLS`：Ascii2D 入口清單，逗號分隔。
- `YANDEX_BASE_URLS`：Yandex 入口清單，逗號分隔。

## 媒體下載設定

- `YTDLP_COOKIES_FILE` 是 yt-dlp 的選填 cookie 檔路徑；檔案存在才會使用。
- `YTDLP_COOKIES_FROM_BROWSER` 可讓 yt-dlp 讀取瀏覽器 cookie，例如 `chrome`、`edge`、`firefox`，下載需要登入或年齡限制內容時建議先填這個。
- `YTDLP_COOKIE` 可直接貼 cookie 字串，IG / TikTok 圖片 fallback 解析時會帶上。
- `INSTALOADER_SESSION_USER` 可讓 Instagram 下載使用本機 Instaloader session；需要先用 `instaloader -l 使用者名稱` 建立。
- `DOUYIN_WTF_API_BASE` 是 TikTok 圖片解析 API，預設使用 `https://douyin.wtf`，也可以改成自己部署的服務。

媒體下載已拆成多個獨立外掛，可以透過功能開關單獨控制：

- X / Twitter：`x:URL`、`回覆搜x`
- 影片平台：`yt:URL`、`回覆搜yt`、`fb:URL`、`回覆搜fb`、`ph:URL`、`回覆搜ph`
- 社群圖片 / 影片：`ig:URL`、`回覆搜ig`、`tk:URL`

## 啟動

需要兩個終端：一個跑 Rasa action server，一個跑 Rasa server。

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

## 熱載入外掛

你可以把新功能寫在 `plugins/` 下面。`HOT_RELOAD_PLUGINS=true` 時，Bot 每次收到訊息會檢查外掛檔案是否更新，有更新就重新載入。

最小範例：

```python
def handle(ctx):
    if ctx.cmd == "ping":
        ctx.reply("pong")
        return True
    return False
```

外掛回傳 `True` 代表指令已處理，訊息不會再送進 Rasa NLU。回傳 `False` 則交給下一個外掛或 Rasa。

## 功能開關

功能定義在 `plugins/core/features.py`。執行時狀態會寫入 `json/features.json`，初始格式可參考 `json/features.example.json`。

常見功能 key：

```text
image_search
engine_saucenao
engine_ascii2d
engine_tracemoe
engine_yandex
engine_iqdb
engine_animetrace
engine_ggjav
x_download
ytdlp_download
facebook_download
instagram_download
tiktok_download
pornhub_download
image_draw_template
freeimage_upload
nhentai
wnacg
jmcomic
pixiv
mention_tools
runtime_tools
search_quota
```

## 常用指令

```text
圖搜說明
回覆搜1 / 回覆搜2 / 回覆搜3 / 回覆搜4 / 回覆搜5 / 回覆搜6 / 回覆搜7
#1 / #2 / #3
#圖片上傳
yt:https://...
fb:https://...
ig:https://...
tk:https://...
x:https://...
ph:https://...
回覆搜yt / 回覆搜fb / 回覆搜ph / 回覆搜ig / 回覆搜x
抽圖 / 隨機圖 / 色圖 / r18色圖 / tag色圖 標籤
n:123456 / n:popular
w:123456
c:123456
p:123456
誰標我 / 清空標註
ren
ping
```

## 第三方項目、許可證與法律注意事項

本專案包含從 `talkouki89/chino-line-image-bot` 搬入並改接 Rasa / LINE 官方 API 的外掛程式碼。第三方來源與 MIT 授權全文放在 `THIRD_PARTY_NOTICES.md`。

### 第三方項目

本專案使用下列第三方項目，請同時遵守各自授權與使用規範：

- [Rasa](https://github.com/RasaHQ/rasa)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [PicImageSearch](https://github.com/kitUIN/PicImageSearch)
- [Lolicon API](https://docs.api.lolicon.app/)
- [jmcomic](https://github.com/hect0x7/JMComic-Crawler-Python)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [douyin.wtf](https://douyin.wtf/)
- [Freeimage.host API](https://freeimage.host/page/api)
- [Instaloader](https://github.com/instaloader/instaloader)

使用前請注意：

- 本專案只提供技術整合範例與自架 Bot 程式碼，不提供、代管或授權任何第三方影音、圖片、漫畫或成人內容。
- `yt-dlp`、`instaloader`、PicImageSearch、Freeimage.host、Lolicon、Pixiv、nHentai、wnacg、jmcomic、Instagram、Facebook、TikTok、X/Twitter、Pornhub 等服務都有各自的服務條款、API 規則、速率限制與內容政策；使用者需要自行確認使用方式是否合法合規。
- 下載、轉傳、公開、儲存或分享任何媒體前，請確認你擁有權利或取得授權，並遵守所在地法律、平台規範與群組規則。
- 成人內容、年齡限制內容或可能違法的內容不應提供給未成年人，也不應在不允許的聊天室或地區使用。
- 若你部署公開 Bot，建議自行加入管理員白名單、功能開關、冷卻時間、日誌保留策略、封鎖清單與內容審核流程。
- `.env` 內的 token、cookie、session、API key 屬於敏感資料，不要提交到 Git，也不要貼到公開 issue 或聊天群。
- 本專案沒有繞過付費牆、DRM、登入限制或平台風控的保證；若第三方服務阻擋、改版或要求登入，對應外掛可能失效。

## 驗證

Windows / Linux / macOS 都相同：

```bash
python -m compileall actions channels chino_rasa plugins plugin_loader.py
rasa data validate
```

如果 `rasa` 無法執行，先確認目前虛擬環境是 Python 3.10。
