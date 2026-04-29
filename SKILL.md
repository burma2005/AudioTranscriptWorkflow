---
name: audio-to-transcript
description: 使用本地 openai-whisper 將語音檔轉錄為逐字稿，並自動摘要成結構化會議紀錄的工作流。
---

# 語音轉逐字稿工作流 (Agent 執行指南)

## 📌 任務目的
此指南指導 Agent 如何使用本地端運行的 `openai-whisper` 套件，將會議錄音或訪談語音檔案（如 `.m4a`、`.mp3` 等）全自動轉錄為 Markdown 格式的逐字稿，並由 Agent 進一步摘要整理為結構化的「會議紀錄」。全程無需依賴任何外部或雲端 API，確保隱私安全。

**注意：為避免移動目錄後路徑失效，所有腳本引用皆為相對路徑，嚴禁寫死絕對路徑。**

## 🚀 Agent 執行步驟 (Workflow)

當收到使用者要求「整理音檔」、「建立會議紀錄」、「轉錄錄音」等指令時，請嚴格按照以下步驟執行：

### 步驟 1：環境相依性檢閱
檢查必備工具是否已安裝：

1. **檢查 Python 套件**：使用 `run_command` 讀取 `requirements.txt` 並安裝。
   ```bash
   pip install -r requirements.txt
   ```
2. **檢查 FFmpeg (Windows)**：若未安裝請使用 `winget`。
   ```bash
   winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
   ```
   > ⚠️ `scripts/transcribe.py` 中已加入動態載入 FFmpeg 的環境變數機制，無需手動修改路徑。

### 步驟 2：背景啟動轉錄腳本與輪詢監控
呼叫專案內建的 `scripts/transcribe.py` 進行轉錄，此為重量運算。

**目錄慣例（相對於專案根目錄）：**
- 🎵 音檔來源：`input/<檔名>.m4a`
- 📄 逐字稿輸出：`output/transcripts/<檔名>_transcript.md`
- 📋 會議紀錄最終輸出：`output/meeting_minutes/<檔名>_minutes.md`

指令範例：
```bash
python scripts/transcribe.py "input/meeting.m4a" "output/transcripts/meeting_transcript.md"
```

- 必須透過 `run_command` 的 `WaitMsBeforeAsync` 將該腳本退至 **背景 (Background) 執行**。
- 透過 `command_status` 定期進行輪詢監控，檢查背景執行序是否完成 (`Exit code: 0`)。
- 腳本預設使用 `language="zh"` 優化繁體中文辨識；若音檔為其他語言，可修改 `transcribe.py` 第 34 行的 `language` 參數。

### 步驟 3：由 Agent 智能生成會議紀錄
一旦 `output/transcripts/` 中的逐字稿產出，Agent 必須呼叫 `view_file` 將其讀入，並根據內容萃取後輸出至 `output/meeting_minutes/<檔名>_minutes.md`。

👉 **結構化的會議紀錄產出強制規範：**
1. **背景基礎資訊**：紀錄會議名稱、日期。
2. **主要討論章節**：依照對話邏輯分區分段撰寫（例如：異常檢討、營運報告、跨部會溝通等）。
3. **重要決議與發言重點**：去除冗詞贅字與語氣詞，將落落長的逐字稿提煉呈俐落的重點條目。
4. **待辦清單 (Action Items)**：強制使用 Markdown 的 Task List (`[ ]`) 撰寫，明確指派負責人與描述行動細節。

### 步驟 4：實施工作區潔淨計畫 (Clean-up)
- 確認 `_會議紀錄.md` 順利產出後，清理過程中的暫存或不需要的佔位檔案。
- 若安裝過程中留下了 `%USERPROFILE%` 與 `%USERP~1` 等快取佔位目錄，應主動尋找並刪除。
