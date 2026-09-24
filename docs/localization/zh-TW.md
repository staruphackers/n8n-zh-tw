# n8n 繁體中文（台灣）在地化

> **狀態：開發中，尚非完整介面或正式部署合格版本。**
> 本文件區分「已有翻譯」、「結構檢查通過」、「實際載入測試」與「全介面驗收」。不得用其中一項取代另一項。

## 目標與不變更的範圍

本專案只將 n8n 的操作介面顯示文字與 README 翻為台灣繁體中文，不修改工作流程執行、節點操作、API、登入驗證、角色權限、企業授權、金鑰或資料庫結構。

不翻譯程式識別字、節點類型 ID、JSON 鍵名、選項儲存值、運算式、程式碼、URL、使用者輸入、工作流程自訂名稱、憑證內容、外部服務回傳資料及原始錯誤細節。

原始 `LICENSE.md`、`LICENSE_EE.md` 及第三方授權聲明保留原文與權利資訊。這不是 n8n 官方繁體中文版，也不提供任何付費功能解鎖。

## 版本基準

本分支建立時的 n8n 原始碼版本為 **2.41.0**，以儲存庫的 `package.json` 為準。原生英文來源位於：

```text
packages/frontend/@n8n/i18n/src/locales/en.json
```

**這不是既有共享主機版本的確認結果。** 部署必須對齊既有服務的確切 n8n 版本及建置方式。不得以 `latest`、相同主版本號或介面看起來相似作為相容證明。

## 翻譯來源與檔案

| 檔案 | 用途 |
| --- | --- |
| `packages/frontend/@n8n/i18n/src/locales/zh-TW.json` | 原生 i18n 基礎介面語言檔；目前仍有缺漏 |
| `localization/zh-TW/overrides.json` | 初始人工翻譯，優先於轉換字典 |
| `localization/zh-TW/patches/*.json` | 依目前英文鍵名新增的人工補譯 |
| `localization/zh-TW/phrase-memory.json` | 英文原文到繁中的翻譯記憶；不是節點或憑證的已安裝語言包 |
| `localization/zh-TW/missing-base.json` | 尚未提供基礎譯文的鍵與原文 |
| `localization/zh-TW/technical-review.json` | 保留原文的技術名稱等候選項目，仍須逐項審閱 |
| `localization/zh-TW/coverage.json` | 產生當下的詳細覆蓋率與錯誤報告 |

`coverage.json` 是產生當下的快照。新增人工補譯後，必須重新產生並驗證，不能直接修改報告中的計數或把 `production_ready` 改為 `true`。

### 固定的 MIT 字典來源

部分譯文由下列**歷史 MIT 版本**的簡體中文原創字典，轉換並調整為台灣用語：

- 專案：`Melaszzzz/n8n-localization`
- 標籤：`v0.3.0`
- 固定 commit：`3b4b5f2e19159009f364d057e24f4b61769c5e43`
- 來源版本基準：其 README 與來源說明列為 n8n `2.34.4`。
- 原始授權與聲明：[`LICENSE`](../../localization/vendor/melas-v0.3.0/LICENSE)、[`NOTICE`](../../localization/vendor/melas-v0.3.0/NOTICE)、[`PROVENANCE.md`](../../localization/vendor/melas-v0.3.0/PROVENANCE.md)。

只採用此固定版本的純文字字典與來源聲明，不採用其安裝器、前端覆蓋腳本或其他執行程式。後續版本的授權可能不同，**不得將下載來源擅自改成 `main`、`latest` 或較新的標籤**。

來源檔案均驗證固定 Git blob 雜湊。轉換工具採用固定版本 OpenCC `0.1.7` 的 `s2twp` 設定與台灣用語表；安裝 wheel 亦驗證 SHA-256。OpenCC 只用於建置翻譯檔，不加入 n8n 執行階段依賴。

只有英文原文完全相符、且保留插值、複數分支、連結與程式碼的譯文才會納入。版本新增文字、衝突或格式不符項目另列待補譯，不會以英文填滿後宣稱翻譯完成。

## 台灣用語

| 英文 | 採用文字 |
| --- | --- |
| Workflow | 工作流程 |
| Node | 節點 |
| Credential | 憑證 |
| Execution | 執行／執行紀錄，依情境區分 |
| Project | 專案 |
| Save / Default / Settings | 儲存／預設／設定 |
| Import / Export | 匯入／匯出 |
| Field / File / Cache | 欄位／檔案／快取 |
| Instance / Server | 執行個體／伺服器 |
| Authentication token | 驗證權杖 |
| Model token | token，避免與驗證權杖混淆 |

產品名稱及 API、JSON、HTTP、MCP、Webhook 等技術名稱可保留英文，但不能將整段未翻譯的操作說明列為技術名稱。

自動簡繁轉換與用語取代不是完整人工校對；仍須確認語意、語氣與實際使用情境。

## 原生載入方式

這版前端依設定呼叫 `setLanguage()`，不會因為新增一個 JSON 檔就自動載入該語言。因此本分支在 `packages/frontend/@n8n/i18n/src/index.ts` 僅新增：

```ts
import traditionalChineseBaseText from './locales/zh-TW.json';
```

並將原有訊息註冊表擴充為：

```ts
messages: { en: englishBaseText, 'zh-TW': traditionalChineseBaseText },
```

英文預設與缺少翻譯時的英文備援維持不變。其餘業務功能程式碼不因語言包而調整。

完成同版本建置及測試後，才在目標服務設定：

```dotenv
N8N_DEFAULT_LOCALE=zh-TW
```

**這個設定本身不會下載或安裝翻譯。** 也不會新增每位使用者各自選語言的功能；它使用既有執行個體語系設定。

## 驗證與重建

在儲存庫根目錄執行：

```sh
# 標準函式庫測試，不連網、不啟動 n8n。
python3 -m unittest discover -s scripts/i18n -p 'test_*.py' -v

# 結構檢查允許部分翻譯；不是完整合格證明。
python3 scripts/i18n/validate_zh_tw.py --allow-partial --report /tmp/n8n-zh-tw-report.json

# 嚴格檢查：缺漏或待審英文仍存在時回傳非零狀態。
python3 scripts/i18n/validate_zh_tw.py
```

驗證項目包含目標 JSON 重複鍵、未知鍵、非字串值、空譯文、每個複數分支的插值、共用文字參照、HTML 標籤與非文字屬性、URL 及程式碼片段。

原始英文檔已有重複鍵。工具會明確列出，並沿用原本 JSON 的後值優先行為，不修改上游英文原檔；繁中目標檔仍不允許任何重複鍵。

產生候選譯文需要網路下載固定來源，請只在開發環境或隔離 CI 執行：

```sh
python3 -m venv /tmp/n8n-zh-tw-tools
/tmp/n8n-zh-tw-tools/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r scripts/i18n/requirements-conversion.txt
/tmp/n8n-zh-tw-tools/bin/python scripts/i18n/import_mit_dictionary.py \
  --output /tmp/n8n-zh-tw-candidates --cache /tmp/n8n-zh-tw-source-cache
```

工具只寫入指定的候選目錄，不修改正在執行的 n8n，也不自動覆蓋儲存庫。人工補譯分檔不得重複鍵名，避免後值默默覆蓋前值。

### CI 的兩種結果

`zh-TW localization structure` 只跑結構測試與部分翻譯統計。

`Build zh-TW dictionary candidates` 另外執行所有候選訊息的 Vue i18n 編譯，以及使用實際 i18n 原始碼的隔離切換測試。其測試依賴版本與完整儲存庫的鎖定相依樹並不等同，**不能取代完整 n8n 建置、型別檢查或瀏覽器端對端測試**。

建置工作只將白名單中的翻譯與來源檔上傳為 Git 物件，不自動移動分支、不合併 PR、不部署。分支更新由明確的檢查與提交步驟完成。

## 仍須完成的範圍

完整基礎文字、節點與憑證、共用元件及硬編碼文字是不同範圍。基礎檔的覆蓋率不可視為全介面覆蓋率。

| 範圍 | 完成條件 |
| --- | --- |
| 基礎介面 | 與当前版本英文葉節點逐項對齊，缺漏為 0，技術保留項目有明確理由 |
| 節點名称與欄位 | 產生並測試目前版本的原生節點翻譯檔，含版本化節點與巢狀欄位 |
| 憑證表單 | 使用原生憑證翻譯載入機制，不改憑證值、認證流程與秘密資訊 |
| 日期、時間及共用元件 | 在實際前端確認 `zh-TW` 支援與備援，不能只看基礎 JSON |
| 硬編碼或外部文字 | 盤點來源，區分可翻譯顯示文字與不可改動的使用者／外部原始資料 |
| 根目錄 README | 全文繁中、連結可用、原有授權與使用限制不遺失 |
| 執行行為 | 同一組工作流程在英文與繁中模式的輸入、輸出、狀態與錯誤行為一致 |

## 共享主機部署指南

### 先確認，不直接覆蓋

需要確認：n8n 確切版本、主機商與控制台、安裝方式（npm、Docker 或原始碼）、應用程式目錄、Node.js 版本、可否 SSH／終端機、可否設定環境變數，以及既有服務的重新啟動方式。

不要提供密碼、SSH 私鑰、資料庫密碼、API 金鑰或完整 `.env`。n8n 的「關於」頁面版本與不含敏感資訊的主機設定畫面即可用於初步對齊。

### 依既有安裝方式選擇產物

| 安裝方式 | 正確方向 | 不應採用的做法 |
| --- | --- | --- |
| 原始碼執行 | 在相同 commit／版本套用翻譯，依原有建置流程建立 i18n 與前端 | 只把 `zh-TW.json` 放進公開網站資料夾 |
| npm 安裝 | 先釐清該版本套件結構，產生對應版本且已驗證的前端／語言產物 | 覆蓋整個 `node_modules`，或假設所有版本路徑一致 |
| Docker | 以相同 n8n 版本建立自訂映像，保留既有持久化 volume 與設定 | 在執行中的容器臨時覆蓋後便當作永久部署 |
| 主機代管且無法修改應用程式檔案 | 向主機商確認自訂前端或自訂映像支援 | 透過網頁檔案管理器上傳 JSON 後期待自動生效 |

優先在本機或隔離 CI 建置，再將經驗證的產物部署至測試環境。共享主機的記憶體與 CPU 限制可能不適合完整 monorepo 建置；不能因為 n8n 已可執行，就推定它也能完成整包建置。

### 備份與回復

部署前保留目前可運作版本、前端檔案、安裝清單、環境變數設定及資料庫／持久化資料的有效備份。使用主機商或資料庫支援的一致性備份方式，不任意複製寫入中的資料庫。

保留原本的 `N8N_ENCRYPTION_KEY`、資料庫設定、`.n8n` 資料及既有工作流程／憑證。這些秘密資訊不得提交到公開 GitHub，也不得因介面翻譯而重設。

測試環境先檢查登入、工作流程清單、編輯畫布、節點與憑證表單、手動測試執行、排程、Webhook、執行紀錄、匯入匯出，以及瀏覽器主控台是否有錯誤。相同工作流程的結果必須與原版一致。

確認通過後，再以主機既有服務管理方式部署並重新啟動；瀏覽器重新載入時排除舊快取。有問題時還原原有前端／映像與語系設定，不變更資料庫或加密金鑰。

**本分支目前沒有執行上述正式主機部署，也沒有宣告可直接上線。**
