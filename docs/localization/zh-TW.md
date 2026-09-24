# n8n 繁體中文（台灣）在地化

> **基礎介面語言檔已補齊；整體介面仍在驗收中，不是正式部署合格證明。**
> 基礎字串、節點與憑證表單、共用元件、硬編碼文字及外部內容是不同範圍。不能以單一語言檔的完整性，宣稱整個 n8n 已完成翻譯。

## 目標與保留範圍

本專案將操作介面與 README 翻為台灣繁體中文，不修改工作流程執行、節點操作、API、登入驗證、角色權限、企业授權或資料庫結構。

不翻譯程式識別字、節點類型 ID、JSON 鍵名、選項儲存值、運算式、程式碼、URL、使用者輸入、工作流程自訂名稱、憑證內容、外部服務回傳資料及原始錯誤細節。

`LICENSE.md`、`LICENSE_EE.md` 與第三方授權聲明保留原文。本專案不是 n8n 官方繁體中文版，也不提供任何付費功能解鎖。

## 版本與成果

分支：`localize/zh-tw-ui`。原始碼版本：**2.41.0**，以本分支的 `package.json` 為準。

基礎英文來源為 `packages/frontend/@n8n/i18n/src/locales/en.json`，共有 **8,927 筆有效葉節點字串**。本分支已提供相同數量的繁中語言項目；品牌、協定與程式範例依明確規則保留原文，不將一般英文句子當成技術名稱放行。

此數字不包含所有節點表單或硬編碼文字。詳細結果請查閱 `localization/zh-TW/coverage.json`；此檔為產生當下的快照，修改翻譯後必須重新驗證。

**2.41.0 不是你既有主機版本的確認結果。** 不得將此分支的前端產物直接覆蓋到不同版本，也不能以相同主版本號作為相容證明。

## 檔案與維護

| 路徑 | 用途 |
| --- | --- |
| `packages/frontend/@n8n/i18n/src/locales/zh-TW.json` | 基礎介面原生語言檔 |
| `packages/frontend/@n8n/i18n/src/index.ts` | 註冊繁中訊息；英文預設與備援保留 |
| `localization/zh-TW/overrides.json` | 初始人工翻譯 |
| `localization/zh-TW/patches/*.json` | 按現行英文鍵名分批補譯 |
| `localization/zh-TW/phrase-memory.json` | 英文原文與繁中譯文的對照記憶 |
| `localization/zh-TW/coverage.json` | 基礎字串覆蓋率、結構與英文保留理由 |
| `localization/zh-TW/missing-base.json` | 尚未提供基礎譯文的項目 |
| `localization/zh-TW/technical-review.json` | 原文保留候選清單，須搭配保留規則判讀，清單不為空不等於漏譯 |
| `scripts/i18n/retained_zh_tw.py` | 精確保留的品牌、協定及指定鍵值範例 |
| `localization/zh-TW/native/*.json` | 節點與憑證的候選翻譯資料；是否可用以產生及載入結果為準 |
| `localization/zh-TW/native-coverage.json` | 同版本節點資料來源、缺漏、歧義與訊息編譯結果 |

新增人工補譯不得與其他分檔重複鍵名。不要直接改生成報告的計數，也不要自行將 `production_ready` 設為 `true`。

### 翻譯來源與授權

部分譯文採用 `Melaszzzz/n8n-localization` 的**歷史 MIT 版本**字典，經 OpenCC 與台灣用語調整，再加上此分支的人工補譯。

固定標籤為 `v0.3.0`；固定 commit 為 `3b4b5f2e19159009f364d057e24f4b61769c5e43`。來源版本以 n8n 2.34.4 為基準；只匯入與本分支英文原文完全相符、且結構合格的譯文。其餘由現行版本原文補譯，不以舊版字典直接覆蓋。

保留的原始聲明：[MIT 授權](../../localization/vendor/melas-v0.3.0/LICENSE)、[NOTICE](../../localization/vendor/melas-v0.3.0/NOTICE)、[PROVENANCE](../../localization/vendor/melas-v0.3.0/PROVENANCE.md)。只採用字典，不執行其安裝器或功能修改腳本。不得將來源改成 `main`、`latest` 或未重新審查授權的新版本。

來源檔案驗證固定 Git blob 雜湊。OpenCC `0.1.7` 使用 `s2twp` 設定，wheel 驗證 SHA-256，只用於建置，不加入 n8n 執行階段依賴。

## 台灣用語

工作流程、節點、憑證、執行紀錄、專案、儲存、預設、設定、匯入、匯出、欄位、檔案、快取、執行個體、伺服器。驗證用 token 翻為「權杖」；模型 token 保留英文，避免混淆。API、JSON、HTTP、MCP、Webhook 與產品名稱可保留。

自動簡繁轉換與用語表不能取代語意及實際介面的人工校對。來源授權聲明保留原文，不做簡繁轉換。

## 載入語系

此版本前端依設定呼叫 `setLanguage()`，不會因新增 JSON 檔就自動載入。因此本分支在原生 i18n 的訊息註冊表加入 `zh-TW`，其餘功能邏輯不變。

完成同版本建置及測試後，才在目標服務設定：

```dotenv
N8N_DEFAULT_LOCALE=zh-TW
```

此設定**不會下載或安裝翻譯**，也不新增每位使用者各自選語言的功能；它沿用既有執行個體的預設語系設定。

## 節點與憑證候選資料

`generate_native_zh_tw.py` 從官方 npm 登錄庫讀取與本分支完全相同版本的 `n8n-nodes-base` 及 `@n8n/n8n-nodes-langchain`。驗證 SHA-512 後，只讀取固定路徑的靜態 JSON 描述，不安裝或執行套件程式。

翻譯只處理節點名稱、說明、欄位標籤、提示、選項顯示名称與按鈕文字，不改 `name`、`value`、`default` 或任何執行條件。不同版本或操作共用相同翻譯路徑、但意思不同時，不猜測應套用哪個版本，會列為歧義。來源版本不可取得時會明確回報，不改抓其他版本。

候選檔不是獨立的外掛安裝包，也不能僅上傳到網站目錄就生效。必須另行確認原生載入路徑及實際節點畫面；仍缺漏的內容不得宣稱已翻譯。

## 檢查與重建

在儲存庫根目錄執行：

```sh
# 離線單元測試
python3 -m unittest discover -s scripts/i18n -p 'test_*.py' -v

# 嚴格基礎字串驗證：缺漏、未核准的英文或結構錯誤均失敗
python3 scripts/i18n/validate_zh_tw.py --report /tmp/n8n-zh-tw-report.json

# 開發中的部分譯文檢查，不可當成完整驗收
python3 scripts/i18n/validate_zh_tw.py --allow-partial
```

驗證包含 JSON 重複鍵、未知鍵、非字串值、空譯文、各複數分支的插值、共用文字參照、HTML 標籤與非文字屬性、URL 及程式碼片段。英文原始檔的既有重複鍵會列報，沿用原本後值優先的解析結果，不修改上游檔案；繁中目標檔不允許重複鍵。

產生候選檔需要下載固定來源，請只在開發環境或隔離 CI 執行：

```sh
python3 -m venv /tmp/n8n-zh-tw-tools
/tmp/n8n-zh-tw-tools/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r scripts/i18n/requirements-conversion.txt
/tmp/n8n-zh-tw-tools/bin/python scripts/i18n/import_mit_dictionary.py \
  --output /tmp/n8n-zh-tw-candidates --cache /tmp/n8n-zh-tw-source-cache
/tmp/n8n-zh-tw-tools/bin/python scripts/i18n/generate_native_zh_tw.py \
  --output /tmp/n8n-zh-tw-candidates
```

工具只寫入候選目錄，不修改執行中的 n8n。CI 另外使用實際 i18n 原始碼測試切換、插值、複數、英文備援及快取，並編譯訊息。隔離測試使用相容版本依賴，但不等於完整儲存庫的鎖定相依樹，不能取代完整建置、型別檢查或瀏覽器端對端測試。

CI 只上傳白名單中的翻譯檔為 Git 物件，不自動更新分支、不合併 PR、不部署。

## 共享主機部署

### 必要資訊

先確認 n8n 的確切版本、主機商／控制台、安裝方式（npm、Docker 或原始碼）、應用程式目錄、Node.js 版本、SSH／終端機權限、環境變數設定及服務重新啟動方式。無須提供密碼、私鑰、API 金鑰或完整 `.env`。

| 現況 | 部署方向 | 不應採用 |
| --- | --- | --- |
| 原始碼執行 | 在同版本套用翻譯，依原有流程建置 i18n 與前端 | 只把 JSON 放入公開網站資料夾 |
| npm 安裝 | 先確認該版本套件結構，部署對應版本且已驗證的產物 | 覆蓋整個 `node_modules` 或猜測前端路徑 |
| Docker | 以相同版本建立自訂映像，保留原有持久化 volume | 在執行中的容器臨時覆蓋便視為永久部署 |
| 代管且不能修改應用程式 | 向主機商確認自訂前端或映像支援 | 假設上傳 JSON 後會自動生效 |

共享主機可執行 n8n，不代表其資源足以建置整個 monorepo。優先在本機或隔離 CI 建置，再部署到同版本測試環境。未完成驗證前不提供通用的直接覆蓋命令。

### 備份、驗收與回復

部署前保留目前可運作版本、前端、安裝清單及有效的資料庫／持久化資料備份。使用支援一致性的備份方法，不任意複製仍在寫入的資料庫。

保留原本的 `N8N_ENCRYPTION_KEY`、資料庫設定、`.n8n` 資料、工作流程與憑證；秘密資訊不得提交至 GitHub，不因翻譯而重設。

測試登入、工作流程清單、畫布、節點及憑證表單、測試執行、排程、Webhook、執行紀錄、匯入匯出與瀏覽器主控台。相同工作流程的輸入、輸出、狀態與錯誤行為應與原版一致。

通過後才依既有服務管理方式部署與重新啟動，並排除瀏覽器舊快取。出現問題時還原原有前端／映像與語系設定，不修改資料庫或加密金鑰。

**目前未部署至使用者的正式主機，完整建置與全介面驗收仍須完成。**
