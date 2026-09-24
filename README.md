![橫幅圖片](https://user-images.githubusercontent.com/10284570/173569848-c624317f-42b1-45a6-ab09-f0ea3c247648.png)

# n8n — AI Agent 與工作流程自動化平台

n8n 是採用 fair-code 授權模式的平台，協助你建置與部署 AI Agent 和工作流程。結合視覺化畫布與自訂程式碼，可自行架設，或使用 [雲端服務](https://app.n8n.cloud/login)，並串接超過 1,500 種整合服務。從原型到正式上線，讓 AI 自動化處理實際工作。

> 本儲存庫是 `staruphackers/n8n-zh-tw` 的繁體中文在地化分支，並非 n8n 官方繁體中文版。目標是翻譯操作介面、原生 i18n 語言包與文件，不修改工作流程執行、節點功能、API、權限或授權機制。目前為開發中版本，不代表所有介面與節點已完成翻譯。部署條件與驗收範圍請參閱 [繁體中文在地化說明](docs/localization/zh-TW.md)。

![n8n.io 操作介面畫面](https://raw.githubusercontent.com/n8n-io/n8n/master/assets/n8n-screenshot-readme.png)

## 主要功能

- **以 AI 為核心的自動化平台**：使用自己的資料、模型與工具，建置並實際運行 AI 工作流程和多步驟 Agent。
- **自由選擇模型，不受供應商綁定**：串接 OpenAI、Anthropic、Google 或開源模型，切換供應商時不必更動架構。
- **從原型到正式上線**：設計包含條件邏輯、工具使用、人工核准與完整可觀測性的多步驟 AI 工作流程。
- **需要時即可撰寫程式碼**：結合視覺化操作、JavaScript、Python 與 npm 套件，打造進階 AI 工作流程。
- **適用企業情境的 AI**：支援自行架設或安全部署、角色型存取控制、稽核軌跡與敏感資料處理。
- **善用既有資源**：透過超過 1,500 種整合服務和 9,000 個[工作流程範本](https://n8n.io/workflows)，將 AI 串接至既有系統。

上述功能與數量沿用此分支所依據的上游 README；實際可用功能仍依 n8n 版本、方案與授權而定。

## 快速開始

以下是上游 n8n 的一般啟動方式，**不會自動安裝本儲存庫的繁體中文語言包**，也不應用來直接取代已在使用的正式服務。

可使用安裝指令碼立即試用 n8n；需要先安裝 [Docker](https://www.docker.com/)。建議先檢視遠端指令碼內容，再決定是否執行：

```sh
curl -fsSL https://get.n8n.io | sh
```

也可依照 [Docker 安裝文件](https://docs.n8n.io/hosting/installation/docker/) 手動部署：

```sh
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

啟動後，開啟 `http://localhost:5678` 進入編輯器。

## 繁體中文在地化

本專案採用台灣繁體中文用語，例如「工作流程」、「節點」、「憑證」、「執行紀錄」、「儲存」、「匯入」、「匯出」、「預設」與「設定」。保留產品名稱、API、JSON、HTTP、Webhook、MCP 等技術名稱。

翻譯只更動顯示文字，不翻譯 JSON 鍵名、程式識別字、API 參數、運算式、網址、使用者輸入或儲存的工作流程資料。

開發基準為此分支的 `package.json`；本次開始作業時的版本為 `2.41.0`。這不是你既有主機版本的確認結果。不得將此分支的前端建置產物直接覆蓋到其他版本。

- [在地化範圍、驗收與共享主機部署注意事項](docs/localization/zh-TW.md)
- [原生 i18n 套件](packages/frontend/@n8n/i18n/README.md)
- [上游 i18n 技術文件](packages/frontend/@n8n/i18n/docs/README.md)

## 參考資源

- 📚 [使用文件](https://docs.n8n.io)
- 🔧 [超過 1,500 種整合服務](https://n8n.io/integrations)
- 💡 [工作流程範例](https://n8n.io/workflows)
- 🤖 [AI 與 LangChain 指南](https://docs.n8n.io/advanced-ai/)
- 👥 [社群論壇](https://community.n8n.io)
- 📖 [社群教學](https://community.n8n.io/c/tutorials/28)

## 支援

需要協助時，可前往社群論壇取得支援，並與其他使用者交流：
[community.n8n.io](https://community.n8n.io)

本儲存庫的翻譯問題請在本儲存庫回報；上游程式問題請先確認是否也發生於相同版本的原版 n8n。

## 授權

n8n 採用 [fair-code](https://faircode.io) 模式，依 [Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) 與 [n8n Enterprise License](https://github.com/n8n-io/n8n/blob/master/LICENSE_EE.md) 發布。

- **原始碼可供檢視**：可查看原始碼。
- **可自行架設**：依授權條款部署於自己的環境。
- **可擴充**：依授權條款新增自己的節點與功能。

若需要額外功能與支援，可洽詢[企業授權](mailto:license@n8n.io)。

更多授權模式資訊請參閱[官方文件](https://docs.n8n.io/sustainable-use-license/)。本地化不變更、移除或繞過任何原有授權、版權聲明或付費功能限制；`LICENSE.md` 與 `LICENSE_EE.md` 保持原文。

## 參與貢獻

發現錯誤 🐛 或有新功能想法 ✨？請閱讀上游[貢獻指南](https://github.com/n8n-io/n8n/blob/master/CONTRIBUTING.md)，了解環境設定與最佳實務。

提交本儲存庫的翻譯時，請保留原始鍵名、插值變數、連結目標、HTML 標籤與複數分支，並在相同版本的測試環境檢查顯示結果。

## 加入 n8n 團隊

想一起打造自動化的未來嗎？歡迎查看 n8n 的[職缺資訊](https://n8n.io/careers)，加入上游團隊。

## n8n 這個名稱代表什麼？

**簡要說明：** n8n 來自「nodemation」，讀作「n-eight-n」。

**完整說明：**「我很常被問到這個問題，比原先預期的還頻繁，因此決定在這裡回答。當初為專案尋找合適名稱與尚未被註冊的網域時，很快就發現能想到的好名字幾乎都有人用了。最後我選擇了 nodemation：『node-』表示它採用節點視圖，也使用 Node.js；『-mation』則來自 automation，也就是這個專案希望協助大家做到的自動化。不過，我不喜歡這個名稱太長，也無法想像每次使用命令列介面時都要輸入這麼長的名字，最後便將它縮成了『n8n』。」

— **Jan Oberhauser，上游 README 所引述的 n8n.io 創辦人暨執行長**
