# VRoid Hair Slot Converter

**English** | [简体中文](#简体中文)

> An unofficial tool. Not affiliated with or endorsed by pixiv or VRoid Studio.

---

## What does this do?

VRoid Studio locks every hair custom item (`.vroidcustomitem`) to the specific hair slot it was originally created for — Front, Back, Sideburns, etc. You cannot import a "Front hair" item into the "Back hair" slot, even if the shape would look perfect there.

This tool rewrites the slot information inside the file so you can use any hair item in any slot.

---

## Requirements

- **Windows** (tested on Windows 10/11)
- **Python 3.8 or newer** — [Download Python](https://www.python.org/downloads/)  
  *(During installation, check ✅ "Add Python to PATH")*
- **VRoid Studio** — [Download VRoid Studio](https://vroid.com/en/studio)

---

## Files in this folder

| File | Purpose |
|------|---------|
| `run_converter.bat` | **Double-click to launch** the graphical converter |
| `vroid_hair_converter_gui.py` | The graphical interface (opened by the .bat file) |
| `vroid_hair_type_converter.py` | The conversion engine |

---

## How to use — Step by step

### Step 1 — Export your hair item from VRoid Studio

In VRoid Studio, go to your character's hair settings, find the item you want to convert, and **export it** as a `.vroidcustomitem` file. Save it anywhere you like.

### Step 2 — Open the converter

Double-click **`run_converter.bat`**.

A window like this will open:

```
┌─────────────────────────────────────────────┐
│  Input file (.vroidcustomitem)              │
│  [ path/to/your/item.vroidcustomitem ] [Browse] │
│                                             │
│  Convert TO slot                            │
│  ● Front (前髪)                              │
│  ○ Back (後ろ髪)                             │
│  ○ Sideburns (横髪)                          │
│  ○ Ahoge (アホ毛)                             │
│  ○ Extensions (エクステ)                      │
│  ○ Extra (ハネ毛)                             │
│  ○ Overall Hair (全体)                       │
│                                             │
│  [ ▶ Convert ]                              │
└─────────────────────────────────────────────┘
```

### Step 3 — Select your file

Click **Browse…** and select the `.vroidcustomitem` file you exported in Step 1.

### Step 4 — Choose the target slot

Select the hair slot you want the item to work in.

### Step 5 — Convert

Click **▶ Convert**. When it's done, a pop-up will confirm success.

The converted file is saved in the **same folder as your original file**, with the slot name added:
```
earphone.vroidcustomitem  →  earphone_Front.vroidcustomitem
```

### Step 6 — Import into VRoid Studio

Open VRoid Studio, go to the matching hair slot, and import the new file. It should load without any compatibility errors.

---

## Available slots

| Slot name | Japanese | Notes |
|-----------|----------|-------|
| Front | 前髪 | Bangs / front hair |
| Back | 後ろ髪 | Back hair |
| Sideburns | 横髪 | Side hair |
| Ahoge | アホ毛 | Antenna hair |
| Extensions | エクステ | Hair extensions (tied) |
| Extra | ハネ毛 | Extra / flyaway hair |
| Overall_Hair | 全体 | Full hairstyle |

---

## Troubleshooting

**"Python was not found" when double-clicking the .bat file**  
→ Install Python from [python.org](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation. Then try again.

**"This item is incompatible" error in VRoid Studio after importing**  
→ Make sure you're importing the file into the correct slot (the one you selected during conversion). For example, a file converted to "Front" must be imported into the Front hair slot.

**The converter window doesn't appear**  
→ Right-click `run_converter.bat` → "Run as administrator" and try again.

---

## Advanced usage (command line)

If you prefer the terminal:
```
python vroid_hair_type_converter.py  myitem.vroidcustomitem  Front
```
Replace `Front` with any slot name from the table above.

---

## Disclaimer

This is an **unofficial, community-made tool** and is not affiliated with, endorsed by, or supported by pixiv Inc. or VRoid Studio. Use at your own risk. Always keep a backup of your original `.vroidcustomitem` files before converting.

---
---

# 简体中文

**[English](#vroid-hair-slot-converter)** | 简体中文

> 非官方工具，与 pixiv 及 VRoid Studio 无任何关联。

---

## 这个工具是做什么的？

VRoid Studio 会将每个发型自定义部件（`.vroidcustomitem` 文件）锁定到它最初创建时所属的发型插槽——前发、后发、侧发等。即使形状完全合适，你也无法把"前发"部件导入"后发"插槽。

本工具会修改文件内部的插槽信息，让你可以将任意发型部件用于任意插槽。

---

## 使用前准备

- **Windows 系统**（已在 Windows 10/11 上测试）
- **Python 3.8 或更高版本** — [下载 Python](https://www.python.org/downloads/)  
  *(安装时请务必勾选 ✅ "Add Python to PATH")*
- **VRoid Studio** — [下载 VRoid Studio](https://vroid.com/en/studio)

---

## 文件夹中的文件说明

| 文件 | 用途 |
|------|------|
| `run_converter.bat` | **双击启动**图形界面转换器 |
| `vroid_hair_converter_gui.py` | 图形界面程序（由 .bat 文件自动打开） |
| `vroid_hair_type_converter.py` | 转换引擎（核心程序） |

---

## 使用步骤

### 第一步 — 从 VRoid Studio 导出发型部件

在 VRoid Studio 中，进入角色的发型设置，找到你想要转换的部件，将其**导出**为 `.vroidcustomitem` 文件。保存到任意位置即可。

### 第二步 — 打开转换器

双击 **`run_converter.bat`**，会弹出如下窗口：

```
┌──────────────────────────────────────────────┐
│  输入文件 (.vroidcustomitem)                  │
│  [ 你的文件路径 ]              [浏览...]       │
│                                              │
│  转换到哪个插槽                               │
│  ● Front（前发）                              │
│  ○ Back（后发）                               │
│  ○ Sideburns（侧发）                          │
│  ○ Ahoge（呆毛）                              │
│  ○ Extensions（延长发/扩展）                  │
│  ○ Extra（翘发/多余发）                        │
│  ○ Overall Hair（全体发型）                   │
│                                              │
│  [ ▶ 转换 ]                                  │
└──────────────────────────────────────────────┘
```

### 第三步 — 选择文件

点击 **浏览…**，选择第一步中导出的 `.vroidcustomitem` 文件。

### 第四步 — 选择目标插槽

选择你希望这个部件能用于的发型插槽。

### 第五步 — 开始转换

点击 **▶ 转换**。完成后会弹出成功提示。

转换后的文件会保存在**与原文件相同的文件夹**中，文件名末尾会加上插槽名称：
```
耳机.vroidcustomitem  →  耳机_Front.vroidcustomitem
```

### 第六步 — 导入 VRoid Studio

打开 VRoid Studio，进入对应的发型插槽，导入新文件。应该可以正常加载，不会出现兼容性错误。

---

## 插槽对照表

| 插槽名称 | 日语 | 说明 |
|----------|------|------|
| Front | 前髪 | 刘海 / 前发 |
| Back | 後ろ髪 | 后发 |
| Sideburns | 横髪 | 侧发 |
| Ahoge | アホ毛 | 呆毛 |
| Extensions | エクステ | 延长发（绑发） |
| Extra | ハネ毛 | 翘发 / 额外发型 |
| Overall_Hair | 全体 | 整体发型 |

---

## 常见问题

**双击 .bat 文件时提示"找不到 Python"**  
→ 请从 [python.org](https://www.python.org/downloads/) 安装 Python，安装时务必勾选"Add Python to PATH"，然后重试。

**导入 VRoid Studio 后提示"此部件不兼容"**  
→ 请确认你是将文件导入到了正确的插槽（即转换时选择的目标插槽）。例如，转换为"Front"的文件必须导入到前发插槽。

**转换器窗口没有弹出**  
→ 右键点击 `run_converter.bat` → 选择"以管理员身份运行"，再试一次。

---

## 命令行使用方式（进阶）

如果你熟悉命令行操作：
```
python vroid_hair_type_converter.py  我的部件.vroidcustomitem  Front
```
将 `Front` 替换为上方表格中的任意插槽名称即可。

---

## 免责声明

本工具为**非官方社区工具**，与 pixiv 株式会社及 VRoid Studio 无任何关联，亦未获得其授权或背书。使用风险自负。转换前请务必备份原始 `.vroidcustomitem` 文件。
