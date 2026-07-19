# Learning OpenCode for Seismology

這是一套以繁體中文編寫的 **OpenCode CLI 實作教材**。內容著重於如何操作 OpenCode、如何寫 prompt、如何建立 agents 與 commands，以及如何把 OpenCode 應用到地震資料、科學論文、監測系統和 GitHub Pages。

## 教學首頁

<https://oceanicdayi.github.io/Learning_opencode/>

> GitHub Pages 必須先在 repository 的 **Settings → Pages → Source** 選擇 **GitHub Actions**。

## 完整指南

- [OpenCode CLI 地震研究實作指南](docs/OPENCODE_GUIDE.md)
- [專案科學與安全規則](AGENTS.md)
- [OpenCode 專案設定](opencode.json)

## 1. 安裝 OpenCode

Linux、macOS、Termux：

```bash
curl -fsSL https://opencode.ai/install | bash
```

或使用 npm：

```bash
npm install -g opencode-ai
```

確認版本：

```bash
opencode --version
opencode --help
```

## 2. 下載專案並啟動

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

`/connect` 用來設定模型供應商；`/init` 會掃描 repository 並建立或補充 `AGENTS.md`。

## 3. 最常用 CLI 指令

```bash
# 啟動互動式 TUI
opencode

# 延續最近 session
opencode -c

# 非互動執行單一任務
opencode run "說明這個 repository 的結構與資料流"

# 指定 Plan agent，不修改檔案
opencode run --agent plan \
  "閱讀 AGENTS.md，規劃地震目錄品質檢查"

# 附加資料檔案
opencode run -f data/sample/catalog.csv \
  "檢查欄位、缺值、重複事件與異常值"

# 列出模型與 agents
opencode models
opencode agent list

# 查看 session、成本與用量
opencode session list
opencode stats

# 更新 OpenCode
opencode upgrade
```

更多指令包括：

```bash
opencode auth login
opencode auth list
opencode agent create
opencode mcp list
opencode export
opencode import session.json
opencode serve
opencode web
opencode attach http://localhost:4096
opencode github install
```

## 4. 建議工作模式

```text
Plan → Build → Reviewer → Test → Commit
```

### Plan

```bash
opencode run --agent plan \
  "閱讀 AGENTS.md、src 與 tests。不要修改檔案；列出方法、風險、預計修改檔案與驗證方式。"
```

### Build

在 TUI 切換到 Build agent：

```text
只實作計畫中的第一個小步驟。加入 unit tests，
不得修改 data/raw，不得 push；完成後執行測試並顯示 diff 摘要。
```

### Reviewer

```text
@scientific-reviewer
檢查資料洩漏、時間窗、單位、樣本數、偏差與過度宣稱。
不要修改檔案。
```

### Test

```bash
python -m unittest discover -s tests -v
python scripts/generate_sample_catalog.py
python scripts/export_web_data.py
git diff --check
```

## 5. 本專案自訂 commands

在 OpenCode TUI 中可直接輸入：

```text
/calculate-mc data/sample/catalog.csv；比較 bin width 0.1 與 0.2
/review-manuscript 特別檢查資料洩漏、空間偏差與時間窗可比性
/build-dashboard 新增逐秒震度時間序列頁面
```

commands 位於：

```text
.opencode/commands/
```

CLI 也可以呼叫：

```bash
opencode run --command calculate-mc \
  "使用 data/sample/catalog.csv，先完成資料品質檢查"
```

## 6. 本專案自訂 agents

```text
@seismic-data          地震資料處理、QC、Mc 與測試
@manuscript-writer     依 repository 證據撰寫論文
@scientific-reviewer   唯讀 SRL reviewer 式審查
```

agents 位於：

```text
.opencode/agents/
```

也可自行建立：

```bash
opencode agent create
opencode agent list
```

## 7. 四個實際案例

### 地震資料處理

```text
@seismic-data
閱讀 data/sample/catalog.csv 與 src/seismo/completeness.py。
先做 schema、時間、經緯度、深度、規模、缺值與重複事件檢查。
再檢查 MAXC binning、tie handling、3 個月移動窗與低樣本標記。
不得修改原始資料；完成後執行 tests。
```

### 科學論文

```text
@manuscript-writer
只根據 src、configs、tests 與 outputs 撰寫 Methods。
不得補寫不存在的方法；未驗證引用標成 [AUTHOR CHECK]。
```

### 監測系統

```text
使用 Plan agent 規劃 Raspberry Pi 地震監測 MVP：
連續波形、ring buffer、每秒震度、資料 gap、斷線恢復、健康監測與中央端 JSON。
先規劃，不寫程式。
```

### 互動網站

```text
/build-dashboard
新增 OpenCode CLI 教學頁面。Python 負責產生科學結果 JSON，
前端只負責視覺化。保持手機友善，完成後執行 tests 與靜態檔案檢查。
```

## 8. 專案目錄

```text
.opencode/agents/    專用 subagents
.opencode/commands/  可重複使用的工作流程
AGENTS.md             專案規則與科學誠信要求
opencode.json         權限與預設 agent 設定
docs/                 完整教學文件
src/seismo/           地震學 Python 範例
tests/                自動測試
scripts/              資料產生與網站輸出
site/                 GitHub Pages 教學網站
.github/workflows/    測試與部署
```

## 9. Prompt 基本公式

```text
目標 + 輸入 + 限制 + 輸出 + 驗證 + 完成回報
```

範例：

```text
閱讀 AGENTS.md、catalog schema、Mc 程式與 tests。
使用 Plan agent，不修改檔案。
檢查 3 個月移動窗 MAXC 是否可重現，
列出時間邊界、binning、樣本數門檻、敏感度分析及驗證方式。
```

避免只輸入：「幫我分析資料並寫論文」。

## 科學限制

repository 中的地震目錄是固定亂數種子產生的教學資料，不是正式觀測。MAXC 適合教學與快速檢查，但正式 completeness 研究仍應比較其他方法、不確定性、樣本數與空間／時間敏感度。
