# OpenCode CLI 地震研究實作指南

本指南聚焦 OpenCode 的使用方法、CLI 指令、TUI 操作、自訂 agent／command，以及地震資料、科學論文、系統建置與互動網站的實際工作流程。

> 指令依 2026-07-19 OpenCode 官方文件整理。OpenCode 更新快速，使用前可執行 `opencode --version` 與 `opencode upgrade`。

---

## 1. 安裝與初始化

### Linux／macOS／Termux

```bash
curl -fsSL https://opencode.ai/install | bash
```

也可使用 npm：

```bash
npm install -g opencode-ai
```

確認安裝：

```bash
opencode --version
opencode --help
```

複製本專案並啟動：

```bash
git clone https://github.com/oceanicdayi/Learning_opencode.git
cd Learning_opencode
opencode
```

第一次進入 TUI：

```text
/connect
/init
```

- `/connect`：連接 OpenCode Zen 或其他模型供應商。
- `/init`：掃描 repository 並建立或補充 `AGENTS.md`。
- `AGENTS.md` 應提交到 Git，讓團隊與不同模型遵循相同研究規則。

---

## 2. CLI 與 TUI 的差別

### TUI：互動式工作

```bash
opencode
opencode /path/to/project
opencode -c
opencode --model provider/model
opencode --agent plan
```

適合：

- 探索 repository。
- 先規劃再逐步修改。
- 檢視 diff、接受或拒絕工具操作。
- 呼叫不同 agents。

### `opencode run`：非互動與自動化

```bash
opencode run "說明這個 repository 的資料流"
```

指定目錄、agent 與模型：

```bash
opencode run \
  --dir . \
  --agent plan \
  --model provider/model \
  "檢查地震資料流程，提出不修改檔案的改善計畫"
```

附加檔案：

```bash
opencode run -f data/sample/catalog.csv \
  "檢查欄位、缺值、重複事件與異常值，只輸出 QC 報告"
```

輸出 JSON 事件，方便其他程式處理：

```bash
opencode run --format json \
  "摘要目前 repository 狀態" > outputs/opencode-events.jsonl
```

延續上一個 session：

```bash
opencode run -c "根據剛才的計畫，列出第一個可安全實作的步驟"
```

使用自訂 command：

```bash
opencode run --command calculate-mc \
  "使用 data/sample/catalog.csv，先檢查資料品質"
```

---

## 3. 常用 CLI 指令速查

| 指令 | 用途 | 地震研究例子 |
|---|---|---|
| `opencode` | 啟動 TUI | 互動檢查專案與修改程式 |
| `opencode run "..."` | 非互動執行 prompt | 批次生成 QC 報告 |
| `opencode -c` | 延續最近 session | 接續昨日的 manuscript 工作 |
| `opencode models` | 列出可用模型 | 找到正確的 `provider/model` 名稱 |
| `opencode auth login` | 登入模型供應商 | 加入 OpenAI、Anthropic 等 provider |
| `opencode auth list` | 查看已登入 provider | 檢查環境是否可用 |
| `opencode agent list` | 列出 agents | 確認 seismic-data／reviewer 是否載入 |
| `opencode agent create` | 互動建立 agent | 建立只讀 SRL reviewer |
| `opencode mcp list` | 查看 MCP | 檢查外部工具連線 |
| `opencode session list` | 列出 sessions | 找回先前研究討論 |
| `opencode export` | 匯出 session JSON | 保存重要方法決策與 prompt |
| `opencode import file.json` | 匯入 session | 在另一台電腦延續工作 |
| `opencode stats` | 查看 token／成本 | 比較各模型使用量 |
| `opencode web` | 啟動 OpenCode Web UI | 手機或區網瀏覽器操作 |
| `opencode serve` | 啟動 headless server | 讓多個 CLI command 共用 backend |
| `opencode attach URL` | TUI 連到既有 server | 從另一台機器操作 |
| `opencode github install` | 安裝 GitHub agent workflow | 在 issue／PR 中使用 OpenCode |
| `opencode upgrade` | 更新 OpenCode | 使用最新 CLI 功能 |

### 長時間批次工作：共用 server

Terminal A：

```bash
opencode serve --port 4096
```

Terminal B：

```bash
opencode run --attach http://localhost:4096 \
  "檢查 tests 是否覆蓋 Mc 邊界條件"
```

這樣可避免每個 `run` 重複啟動 backend 或 MCP。

### 手機／區域網路操作

```bash
export OPENCODE_SERVER_PASSWORD='請換成強密碼'
opencode web --hostname 0.0.0.0 --port 4096
```

同一區域網路中的瀏覽器可用電腦 IP 連線。不要把未設密碼的服務直接暴露到公開網路。

---

## 4. TUI 常用指令

| TUI 指令 | 功能 |
|---|---|
| `/connect` | 連接模型供應商 |
| `/init` | 掃描專案並建立 `AGENTS.md` |
| `/help` | 顯示 TUI 指令與快捷鍵 |
| `/undo` | 撤銷 OpenCode 最近變更 |
| `/redo` | 重做被撤銷變更 |
| `/share` | 產生目前 session 分享連結；本專案預設停用 |
| `/calculate-mc` | 本專案自訂 Mc 工作流程 |
| `/review-manuscript` | 本專案自訂 SRL reviewer 審查 |
| `/build-dashboard` | 本專案自訂網站更新流程 |

其他重要操作：

- 使用 `Tab` 在主要 agents（例如 Plan、Build）間切換。
- 在輸入中使用 `@檔案` 搜尋並加入特定檔案。
- 使用 `@seismic-data`、`@scientific-reviewer` 等方式呼叫 subagent。

---

## 5. 建議工作模式：Plan → Build → Review → Test

### Step 1：Plan，不修改檔案

```text
使用 Plan agent。閱讀 AGENTS.md、README、src、tests 與資料 schema。
不要修改檔案。說明：
1. 現況與資料流
2. 科學假設
3. 風險與失敗案例
4. 預計修改檔案
5. 驗證方法
```

CLI：

```bash
opencode run --agent plan \
  "閱讀 AGENTS.md，規劃地震目錄 QC；不要修改檔案"
```

### Step 2：Build，小步實作

```text
切換 Build agent。只實作剛才計畫中的第一項：
建立 catalog schema validator 與 unit tests。
不得修改 data/raw，不得 push。
完成後執行測試並顯示 diff 摘要。
```

### Step 3：Reviewer，唯讀挑戰

```text
@scientific-reviewer
檢查剛才的實作是否存在單位錯誤、時間格式問題、資料洩漏、
樣本數不足或不當科學假設。不要修改檔案。
```

### Step 4：Test 與提交

```bash
python -m unittest discover -s tests -v
python scripts/generate_sample_catalog.py
python scripts/export_web_data.py
git diff --check
git status
```

確認後才自行 commit／push。

---

## 6. 案例一：處理地震目錄

### 互動式使用

```bash
opencode
```

在 TUI 輸入：

```text
@seismic-data
閱讀 AGENTS.md 與 data/sample/catalog.csv。
先檢查欄位、ISO 時間、經緯度、深度、規模、缺值、重複事件及樣本數。
不要修改原始資料。

接著檢查 src/seismo/completeness.py：
- MAXC binning 是否正確
- tie 時如何處理
- 3 個月移動窗是否有 off-by-one
- 樣本不足時的品質標記

最後執行 tests，輸出問題、修改建議及可接受標準。
```

### 使用自訂 command

```text
/calculate-mc data/sample/catalog.csv；比較 bin width 0.1 與 0.2 的敏感度
```

### 非互動批次 QC

```bash
mkdir -p outputs
opencode run \
  --agent seismic-data \
  -f data/sample/catalog.csv \
  --format json \
  "只做資料品質檢查，不修改檔案；輸出可機器解析的問題清單" \
  > outputs/catalog-qc.jsonl
```

### 建議拆成的任務

1. schema 與單位檢查。
2. 重複事件與異常值。
3. 規模頻度分布。
4. Mc 方法與敏感度。
5. 事件地圖與時間序列。
6. 可重現報告與 tests。

不要只輸入「幫我分析地震資料」；應明確指定輸入、方法、限制、輸出與驗證。

---

## 7. 案例二：撰寫科學論文

### 先建立證據索引

```bash
opencode run --agent plan \
  "閱讀 manuscript、src、configs、tests、outputs。建立 evidence matrix：每項論文主張對應程式、輸入、圖表與限制。不要修改正文。"
```

### 撰寫 Methods

```text
@manuscript-writer
只根據 src、configs、tests 與 outputs 撰寫 manuscript/methods.md。
不得描述 repository 中不存在的方法。
所有參數指出檔案來源；未驗證引用標成 [AUTHOR CHECK]。
```

### Reviewer 式審查

```text
/review-manuscript 特別檢查：
相同時間窗在不同震源距離測站是否包含可比較的 P/S 波資訊；
event-level 與 station-level split 是否有洩漏；
震度四級以上警報門檻的 metrics 是否合理。
```

### CLI 批次審查

```bash
opencode run \
  --agent scientific-reviewer \
  -f manuscript/manuscript.md \
  "輸出 Major comments、Minor comments、必要補充實驗及每項完成標準；不要修改檔案" \
  > manuscript/review-round-01.md
```

> 正式論文中不得讓 agent 憑記憶生成引用或數值。引用、結果與 novelty claim 必須由研究者驗證。

---

## 8. 案例三：建置地震監測系統

### 先規劃架構

```bash
opencode run --agent plan \
  "規劃 Raspberry Pi 地震監測 MVP：連續波形輸入、每秒震度、品質控制、buffer、斷線恢復、健康監測與中央端 JSON。不要寫程式。"
```

### 逐元件開發

```text
使用 Build agent，只實作 waveform buffer：
- 固定長度 ring buffer
- 明確單位與 sampling rate
- gap／overlap handling
- unit tests
- 不實作 trigger 或網路傳輸
```

下一輪再做：

```text
只實作 system health JSON schema 與 validator。
測試 CPU、磁碟、最後資料時間、資料 gap 與 process status。
```

避免一次要求「完成整個 EEW 系統」。將系統拆成接收、QC、計算、輸出、監控與部署，每個步驟都要有 tests 與失敗處理。

---

## 9. 案例四：建立互動網站並部署 GitHub Pages

### 讓 OpenCode 規劃

```text
使用 Plan agent。閱讀 site、scripts/export_web_data.py 與 GitHub workflow。
規劃新增逐秒震度時間序列頁面。
要求 Python 產生 JSON，前端只視覺化；列出 schema、檔案、測試及手機版風險。
```

### 使用自訂 command

```text
/build-dashboard 新增 OpenCode CLI 教學首頁，保留地震資料流程作為實作案例
```

### 本機驗證

```bash
python scripts/generate_sample_catalog.py
python scripts/export_web_data.py
python -m unittest discover -s tests -v
python -m http.server 8000 --directory site
```

### 請 OpenCode 檢查 workflow

```bash
opencode run -f .github/workflows/deploy-pages.yml \
  "審查 GitHub Pages workflow：權限、artifact path、pull_request 條件與失敗處理；不要修改"
```

---

## 10. 自訂 commands

專案 command 放在：

```text
.opencode/commands/
```

例如 `.opencode/commands/catalog-qc.md`：

```markdown
---
description: 檢查地震目錄資料品質
agent: seismic-data
---

閱讀 AGENTS.md 與指定 catalog。
檢查 schema、時間、單位、缺值、重複事件、地理範圍與異常值。
不要修改原始資料。輸出問題、嚴重度、證據、建議與驗證方式。

輸入：$ARGUMENTS
```

使用：

```text
/catalog-qc data/sample/catalog.csv
```

CLI 使用：

```bash
opencode run --command catalog-qc "data/sample/catalog.csv"
```

command 適合把經常重複、需要固定品質標準的工作變成可重用流程。

---

## 11. 自訂 agents

專案 agent 放在：

```text
.opencode/agents/
```

也可互動建立：

```bash
opencode agent create
opencode agent list
```

只讀 reviewer 範例：

```markdown
---
description: 唯讀地震學 reviewer
mode: subagent
temperature: 0.1
tools:
  write: false
  edit: false
---

檢查資料洩漏、偏差、方法與結論，但不要修改檔案。
```

使用：

```text
@scientific-reviewer 審查 manuscript/manuscript.md
```

建議 agents 分工：

- `seismic-data`：資料處理、QC、統計、tests。
- `manuscript-writer`：根據已驗證證據撰寫。
- `scientific-reviewer`：唯讀挑戰方法與論述。
- Plan：架構、風險與工作拆解。
- Build：實際修改與執行測試。

---

## 12. 高品質 prompt 模板

```text
閱讀 AGENTS.md 與 [檔案／資料]。

目標：
[單一、可驗證的目標]

輸入：
[路徑、schema、時間範圍、單位]

限制：
- 不修改 data/raw
- 不捏造資料、結果或引用
- 先規劃，再修改
- 不 push／deploy

輸出：
[程式、CSV、JSON、圖、Markdown 報告]

驗證：
[tests、指標、邊界案例、人工檢查]

完成後回報：
1. 修改檔案
2. 執行命令
3. 測試結果
4. 科學假設
5. 未解決限制
```

差的 prompt：

```text
幫我分析資料並寫論文。
```

較好的 prompt：

```text
使用 Plan agent，讀取 catalog schema、Mc 程式與 tests。
不要修改檔案。檢查 3 個月移動窗 MAXC 是否可重現，
列出時間邊界、binning、樣本數門檻與敏感度分析計畫。
```

---

## 13. 本專案的建議練習順序

1. `opencode`、`/connect`、`/init`。
2. 用 `@檔案` 請 OpenCode 解釋 `src/seismo/completeness.py`。
3. 切 Plan agent，規劃一個小修改。
4. 切 Build agent，加入測試再修改。
5. 執行 `/calculate-mc`。
6. 用 `@scientific-reviewer` 審查結果。
7. 用 `opencode run` 自動輸出 QC 報告。
8. 建立自己的 `.opencode/commands/catalog-qc.md`。
9. 匯出 session 保存研究決策。
10. 更新網站並由 GitHub Actions 驗證。
