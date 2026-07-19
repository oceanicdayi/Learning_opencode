# Learning OpenCode for Seismology

這是一個以繁體中文整理的 OpenCode 地震學實作專案，示範如何用 AI coding agent 完成：

- 地震目錄品質檢查與最小完整規模 Mc 分析
- 可重現的 Python 科學計算與測試
- 科學論文撰寫與 reviewer 式審查
- 地震監測系統架構設計
- 互動式資料網頁與 GitHub Pages 自動部署

## 線上網站

部署完成後：<https://oceanicdayi.github.io/Learning_opencode/>

## 第一版 MVP

第一版使用**程式產生的合成示範目錄**，不是中央氣象署或其他機構的正式觀測資料。分析流程每月計算一次 Mc，使用 3 個月移動時間窗，並以 MAXC 方法估算。

## 本機執行

```bash
python scripts/generate_sample_catalog.py
python scripts/export_web_data.py
python -m unittest discover -s tests -v
python -m http.server 8000 --directory site
```

開啟 `http://localhost:8000`。

## OpenCode 使用

```bash
opencode
```

進入專案後先閱讀 `AGENTS.md`，再使用 `.opencode/commands/` 中的任務模板。

## 目錄

```text
.opencode/          OpenCode agents 與 commands
configs/            科學分析設定
data/sample/        合成示範資料
scripts/            資料產生與網頁輸出
src/seismo/         可重用地震學模組
tests/              自動測試
site/               GitHub Pages 靜態網站
manuscript/         論文工作區
.github/workflows/  CI 與 Pages 部署
```

## 科學限制

MAXC 適合教學與快速檢視，但不應單獨作為正式 catalog completeness 結論。真實研究應比較 GFT、EMR、MBASS 或其他方法，並進行不確定性、樣本數、時間窗與空間敏感度分析。
