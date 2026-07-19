---
description: 檢查地震目錄並計算每月 3 個月移動窗 Mc
agent: seismic-data
---

閱讀 AGENTS.md 與目前資料 schema。先檢查輸入目錄的時間、規模、缺值、重複事件與樣本數，再執行 Mc 分析。

要求：
- 每月計算一次。
- 使用 3 個月移動時間窗。
- 至少回報 MAXC、bin width、樣本數與品質標記。
- 產出 CSV／JSON 與 Mc 隨時間變化圖。
- 不得修改原始資料。
- 完成後執行測試並說明 MAXC 的研究限制。

輸入或補充要求：$ARGUMENTS
