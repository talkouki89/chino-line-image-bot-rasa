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
- 群組工具：歡迎訊息、群組專用發話名稱與頭像、標註查詢。
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
│  └─ group_settings.example.json   # 群組歡迎訊息/外觀設定範例
├─ pic/                             # README / GitHub 顯示圖片
│  └─ github.png                    # README 預覽圖
├─ plugins/                         # 所有可熱加載插件
│  ├─ admin_profile_tools.py        # 管理員 MID、聯絡人、群組 ID、speedtest 工具
│  ├─ example.py                    # ping/pong 範例插件
│  ├─ facebook_download.py          # fb: Facebook 影片下載
│  ├─ freeimage_upload.py           # #圖片上傳，回覆圖片後上傳 Freeimage.host
│  ├─ group_settings.py             # 群組歡迎訊息、群組專用 Bot 名稱/頭像
│  ├─ help_tools.py                 # 圖搜說明、功能狀態、功能設定、功能切換
│  ├─ image_draw_template.py        # 抽圖 / 標籤抽圖 Flex 模板與 Lolicon API
│  ├─ image_search.py               # 回覆圖片圖搜、模板搜、PicImageSearch 調用
│  ├─ instagram_download.py         # ig: Instagram 圖片 / 影片下載
│  ├─ jmcomic_lookup.py             # c: 禁漫天堂解析
│  ├─ nhentai.py                    # nHentai 編號解析與 Popular Now
│  ├─ pixiv_lookup.py               # p: Pixiv 作品解析
│  ├─ pornhub_download.py           # ph: Pornhub 影片下載
│  ├─ reply_media_download.py       # 回覆搜 yt/fb/ph/ig
│  ├─ runtime_tools.py              # ren 運行時間模板
│  ├─ restart_tools.py              # reb @bot 重啟 Rasa server
│  ├─ tiktok_download.py            # tk: TikTok 圖片 / 影片下載
│  ├─ wnacg.py                      # w: 紳士漫畫解析
│  ├─ x_download.py                 # x:URL / 回覆搜x
│  ├─ ytdlp_download.py             # yt:URL 與 yt-dlp 共用下載工具
│  ├─ version_tools.py              # 版本檢查 / 版本更新
│  └─ core/                         # 插件共用工具
│     ├─ cooldown.py                # 抽圖冷卻
│     ├─ features.py                # 功能開關定義與讀寫
│     ├─ freeimage.py               # Freeimage.host API client
│     ├─ gallery_template.py        # 作品解析 Flex 模板
│     ├─ help_template.py           # 說明 / 狀態 / 版本 / 開關 Flex 模板
│     ├─ template.py                # 圖搜結果 Flex 模板
│     ├─ text_convert.py            # 繁簡轉換
│     └─ web_image_search.py        # GGJAV 等網頁圖搜輔助
├─ scripts/                         # 啟動與維護腳本
│  ├─ cleanup_runtime.py            # 清理 logs/ 與 public/media/
│  ├─ cleanup_runtime.ps1           # Windows 清理入口
│  ├─ cleanup_runtime.sh            # Linux/macOS 清理入口
│  ├─ start_action_server.ps1       # 啟動 Rasa action server
│  ├─ start_action_server.sh        # Linux/macOS 啟動 action server
│  ├─ start_cloudflare_tunnel.ps1   # 啟動 Cloudflare Tunnel
│  ├─ start_cloudflare_tunnel.sh    # Linux/macOS 啟動 Cloudflare Tunnel
│  ├─ start_rasa_server.ps1         # 啟動 Rasa server
│  └─ start_rasa_server.sh          # Linux/macOS 啟動 Rasa server
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
# [必填] LINE Developers > Messaging API > Channel access token。
# 這是 Bot 回覆、推送訊息、下載使用者傳來圖片/影片時使用的 token。
LINE_CHANNEL_ACCESS_TOKEN=

# [必填] LINE Developers > Basic settings > Channel secret。
# Webhook 會用它驗證 X-Line-Signature，確認請求真的來自 LINE。
LINE_CHANNEL_SECRET=

# [必填] 最高管理員的 LINE 官方 Messaging API userId。
# 必須是 U 開頭的 userId，不是舊版 CHRLINE MID。
# 不確定自己的值時，在 LINE 對 Bot 輸入：mymid
Creator=

# [建議] 額外管理員 userId，多個用英文逗號分隔。
# 範例：ADMIN_USER_IDS=Uxxxx,Uyyyy
# 管理員可以使用功能設定、群組歡迎訊息、群組 Bot 外觀等管理指令。
ADMIN_USER_IDS=

# [必填] 對外公開 HTTPS 網址，不要加結尾斜線。
# LINE webhook、圖片/影片暫存公開網址都會用它。
# 範例：PUBLIC_BASE_URL=https://chinobot.dpdns.org
PUBLIC_BASE_URL=https://你的網域

# [選填] Bot 使用的時區。
# 預設是台灣時間；也可填 UTC+8。
BOT_TIMEZONE=Asia/Taipei

# [建議] 是否啟用 plugins/ 熱加載。
# true：修改插件後，下次訊息會自動重新載入插件。
# false：插件只在服務啟動時載入。
HOT_RELOAD_PLUGINS=true

# [選填] Linux/VPS 使用「版本更新」或「reb @bot」自動重啟時的 systemd 服務名稱。
# Windows 不用填。
RASA_SYSTEMD_SERVICE=
```

常用選填：

```env
# [選填] SauceNAO API key。
# 使用 SauceNAO 圖搜時建議填寫，沒有 key 可能會受限。
SauceNAO_api_key=

# [選填] Freeimage.host API key。
# 使用 #圖片上傳 時需要。
FREEIMAGE_API_KEY=

# [選填] PicImageSearch 代理。
# 範例：PICSEARCH_PROXIES=http://127.0.0.1:7890
PICSEARCH_PROXIES=

# [選填] PicImageSearch timeout 秒數。
# 網路慢或代理慢時可以調大。
PICSEARCH_TIMEOUT=60

# [選填] yt-dlp cookie 檔案路徑。
# 下載 YouTube / X / Instagram 等需要登入或年齡驗證內容時可用。
# 如果這個檔案存在，會只使用它；不存在才會改用下方瀏覽器 cookie 設定。
YTDLP_COOKIES_FILE=cookies.txt

# [選填] 讓 yt-dlp 從本機瀏覽器讀 cookie。
# 常見值：chrome、edge、firefox；也可用 chrome:Default。
# 注意：在伺服器或無桌面環境通常不能用。
YTDLP_COOKIES_FROM_BROWSER=

# [選填] YouTube 出現「Sign in to confirm」或 bot 驗證時，自動嘗試瀏覽器 cookie。
YTDLP_AUTO_BROWSER_COOKIES=true

# [選填] 自動嘗試的瀏覽器 cookie 來源；分號分隔多組，逗號分隔參數。
YTDLP_AUTO_BROWSER_COOKIE_SOURCES=edge;chrome;firefox

# [選填] 直接填入 cookie 字串。
# 沒有 cookies.txt 時，yt-dlp 會用它當 Cookie header；IG / TikTok fallback 也會用到。
# 不要提交到 Git。
YTDLP_COOKIE=

# [選填] Instaloader session 使用者名稱。
# 若 Instagram 下載需要登入，先在本機執行 instaloader -l 使用者名稱 建立 session。
INSTALOADER_SESSION_USER=

# [選填] nHentai cookie。
# 遇到 403、Cloudflare 或需要登入時可填；不要提交到 Git。
NHENTAI_COOKIE=

# [選填] TikTok / Douyin 解析 API base URL。
# 預設使用 https://douyin.wtf。
DOUYIN_WTF_API_BASE=https://douyin.wtf
```

進階選填：

```env
# [選填] 兼容舊設定名稱；新專案優先使用 LINE_CHANNEL_ACCESS_TOKEN。
LINE_ACCESS_TOKEN=

# [選填] 舊版管理員欄位，仍會被讀取。
# 建議新設定改用 ADMIN_USER_IDS。
ADMIN_MIDS=

# [選填] yt-dlp 執行檔名稱或完整路徑。
YTDLP_BIN=yt-dlp

# [選填] 是否驗證 PicImageSearch HTTPS 憑證。
PICSEARCH_VERIFY_SSL=true

# [選填] Ascii2D base URL，可用逗號分隔多個備援。
ASCII2D_BASE_URLS=https://ascii2d.net

# [選填] Yandex base URL，可用逗號分隔多個備援。
YANDEX_BASE_URLS=https://yandex.ru,https://ya.ru

# [選填] Speedtest 測試下載 URL。
SPEEDTEST_URL=https://speed.cloudflare.com/__down?bytes=10000000

# [選填] 清理 logs/ 保留天數。
CLEANUP_LOG_DAYS=14

# [選填] 清理 public/media/ 保留小時。
CLEANUP_PUBLIC_HOURS=48
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

也可以使用：

```bash
chmod +x scripts/*.sh
./scripts/start_action_server.sh
./scripts/start_rasa_server.sh
./scripts/start_cloudflare_tunnel.sh
```

## Cloudflare Tunnel

如果你已經把網域接到 Cloudflare，建議使用 Named Tunnel，網址才會固定。

### Linux 安裝 cloudflared

Debian / Ubuntu：

```bash
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update
sudo apt install cloudflared
```

建立並綁定 Tunnel：

```bash
cloudflared tunnel login
cloudflared tunnel create chino-line-image-bot-rasa
cloudflared tunnel route dns chino-line-image-bot-rasa chinobot.dpdns.org
```

建立 `~/.cloudflared/config.yml`：

```yaml
tunnel: chino-line-image-bot-rasa
credentials-file: /home/你的使用者/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: chinobot.dpdns.org
    service: http://localhost:5005
  - service: http_status:404
```

啟動：

```bash
cloudflared tunnel run chino-line-image-bot-rasa
```

安裝成 systemd 服務：

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
sudo systemctl status cloudflared
```

LINE Developers Webhook URL 維持：

```text
https://chinobot.dpdns.org/webhooks/line/webhook
```

### VPS 與 endpoints.yml

如果 Rasa server 和 action server 都在同一台 VPS，`endpoints.yml` 可以維持：

```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

只有在 action server 跑在另一台機器、Docker 另一個 service、或不同 port 時才需要改，例如：

```yaml
action_endpoint:
  url: "http://rasa-action:5055/webhook"
```

不要把 `endpoints.yml` 的 action endpoint 設成 Cloudflare 公開網域，除非 action server 真的獨立部署且有安全控管。

## systemd 範例

`/etc/systemd/system/chino-rasa.service`：

```ini
[Unit]
Description=Chino Rasa Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/chino-line-image-bot-rasa
Environment=PYTHONUTF8=1
Environment=PYTHONIOENCODING=utf-8
ExecStart=/opt/chino-line-image-bot-rasa/.venv/bin/python -m rasa run --enable-api --credentials credentials.yml --endpoints endpoints.yml --port 5005
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/chino-action.service`：

```ini
[Unit]
Description=Chino Rasa Action Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/chino-line-image-bot-rasa
Environment=PYTHONUTF8=1
Environment=PYTHONIOENCODING=utf-8
ExecStart=/opt/chino-line-image-bot-rasa/.venv/bin/python -m rasa run actions --port 5055
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

啟用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now chino-action chino-rasa
```

若要讓 `reb @bot` 與 `版本更新` 自動重啟 Rasa server，`.env` 加：

```env
RASA_SYSTEMD_SERVICE=chino-rasa.service
```

## 定期清理 logs 與 public/media

下載功能會把媒體暫存到 `public/media/` 給 LINE 讀取；插件錯誤會追加到專案根目錄的 `errorLog.txt`。服務長期運作時建議定期清理。

手動清理：

```bash
./scripts/cleanup_runtime.sh --log-days 14 --public-hours 48
```

Windows：

```powershell
.\scripts\cleanup_runtime.ps1 --log-days 14 --public-hours 48
```

這會清理 `logs/`、超過保留天數的 `errorLog.txt`，以及超過保留時間的 `public/media/`。

Linux cron 每天 04:30 清理：

```cron
30 4 * * * cd /opt/chino-line-image-bot-rasa && ./.venv/bin/python scripts/cleanup_runtime.py --log-days 14 --public-hours 48 >> logs/cleanup.log 2>&1
```

## Postback 按鈕

功能開關模板與抽圖模板的按鈕已改成 LINE postback：

- 不會在聊天室送出一串指令文字。
- Bot 會在 webhook 內把 postback 轉成內部指令。
- 功能開關使用 `action=toggle_feature&key=<feature_key>`。
- 抽圖模板使用 `cmd=抽圖`、`cmd=r18色圖`、`cmd=tag色圖 標籤`。

## 歡迎訊息

Bot 被邀請進群組或多人聊天室時，會先回覆：

```text
感謝使用此機器
使用方式：輸入「圖搜說明」查看指令
GitHub：https://github.com/talkouki89/chino-line-image-bot-rasa
```

一般用戶可在群組內設定歡迎訊息：

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

一般用戶可在群組內設定：

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
ren
mymid / gid / speedtest
mid:USER_ID / Contact @使用者
版本檢查 / 版本更新
reb @bot
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
