---
title: "客戶端與電腦設定"
description: "在 Windows 和 Linux 上運行客戶端、在規則範圍內多開、UI 縮放，以及無需管理員權限啟動。"
weight: 24
---

# 客戶端與電腦設定

運行 Perpetuum 客戶端的實用說明。

## 先了解規則

多開（多個客戶端控制多個角色）在**一定限制內**是允許的。操作前需了解的公平遊戲規則：

- **嚴禁使用任何自動化或多客戶端控制軟體。**
- **同時活躍的帳號不得超過 5 個。**
- 不得使用虛假、無效或無法接收郵件的電子郵件地址註冊帳號——該地址必須是您本人擁有的。

違規將導致立即永久封號。

## Windows：多個客戶端

1. 安裝 Perpetuum Steam 客戶端。
2. 確認遊戲資料夾中包含一個內容為 `223410` 的 `steam_appid.txt` 檔案。
3. 每增加一個客戶端，複製一份完整的 `Perpetuum` 資料夾。
4. 在每個複製的資料夾中運行 `Perpetuum.exe`（可選：將複製的資料夾作為非 Steam 遊戲添加到 Steam）。

**磁碟空間：** `Layers.gbf` 和 `Perpetuum.gbf` 檔案體積較大且在每個複製中完全相同——請將它們設為符號連結（`mklink`）或捷徑，使其只儲存一份。

## Linux：多個客戶端

每個客戶端複製需要使用**不同的 Proton 版本**，否則將拒絕運行：

1. 照常安裝 Steam 和 Perpetuum；驗證 `steam_appid.txt`（`223410`）。
2. 為每個客戶端複製一份 `Perpetuum` 資料夾。
3. 在登入 Steam 的狀態下，安裝數個較新的 Proton 版本（透過 Steam、手動安裝，或使用 GloriousEggroll 構建版）。
4. 將每個複製作為非 Steam 遊戲添加到 Steam，指向其 `Perpetuum.exe`。
5. 在每個複製的啟動選項中強制指定**不同的 Proton 版本**。
6. 先啟動真正的 Steam 應用程式，再啟動各複製。

疑難排解：

- 選擇 Proton 版本**不會**自動安裝它——您必須在選定該版本後啟動一次遊戲。
- 如果真正的 Steam 應用程式無法啟動，請先以安全模式啟動。
- 自 Proton 5.0 起，DirectX 9/12 模擬運行在 **Vulkan** 上。沒有支援 Vulkan 的 GPU？請在每個複製的啟動選項中添加 `PROTON_USE_WINED3D=1 %command%`。
- 出現帶有紅色警告的空白文字框：請安裝 `libfreetype6:i386`（適用於基於 Debian/Ubuntu 的發行版）。

## UI 縮放

客戶端使用固定像素的 UI，不支援動態縮放。替代方案：

- **低解析度全螢幕**——以低於顯示器解析度的設定進入全螢幕模式，讓 UI 拉伸以填滿畫面（視窗模式和無邊框模式始終使用原生解析度）。降低顯示器本身的解析度也能達到相同效果。
- **UI 縮放工具**——例如 Lossless Scaler（Steam、Windows）：以基礎尺寸以視窗模式運行客戶端，在縮放工具中設定自訂縮放比例，觸發縮放並聚焦客戶端視窗。需預期平滑度與文字清晰度之間的取捨。
- **系統放大鏡**——使用 Windows 放大鏡（或等效工具）進行偶爾的細部閱讀。

## 無需管理員權限啟動

1. 將客戶端檔案從 Steam 資料夾複製到可寫入的位置。
2. 在該位置建立一個 `Perpetuum.bat`，內容為
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`。
3. 透過批次檔啟動。

<!--
開發者備註：2026 年以原創文字重寫。早期版本改編自 Open Perpetuum 社群 wiki（perpetuum.miraheze.org：Multi-Boxing、Linux Setup、Client UI Scaling、Launching without Admin Rights）；該文字已被完全替換，未予沿用。這些是針對零售版 Steam 客戶端構建的客戶端端操作步驟；此處內容無法從本伺服器後端驗證，亦未宣稱任何伺服器功能。Reshader（圖形模組）被刻意排除：它針對零售版客戶端構建，並非 OPP 伺服器功能。
-->