# MarkItDown Desktop

基于微软开源 [markitdown](https://github.com/microsoft/markitdown) 的 Windows 桌面客户端，将 PDF / Word / PPT / Excel / 图片等文档一键转换为干净的 Markdown。

## 特性

- **一键转换** — 拖拽文件或点击选择，一键转为 Markdown
- **文本直转** — 粘贴 HTML / CSV / JSON / XML 等文本，直接转 Markdown
- **美观界面** — 现代化渐变 UI，卡片式布局，流畅动画
- **无需配置** — 打包为独立 `.exe`，双击即可运行，无需安装 Python
- **多格式支持** — PDF、DOCX、PPTX、XLSX、HTML、图片、CSV、JSON 等

## 截图

```
┌─────────────────────────────────────────────┐
│  MarkItDown · 智能文档转换                     │  ← 渐变标题栏
├─────────────────────────────────────────────┤
│  [文件转换] [文本直转]                         │  ← Tab 切换器
├─────────────────────────────────────────────┤
│                                             │
│        📁  拖拽文件到此处                     │  ← 拖拽区
│           或点击下方按钮选择文件               │
│           支持 PDF / Word / PPT / Excel ...  │
│                                             │
├─────────────────────────────────────────────┤
│  [选择文件] [一键转换] [清除选择]              │  ← 操作按钮
├─────────────────────────────────────────────┤
│  ● 准备就绪                                  │  ← 状态指示
│  ▓▓▓▓▓▓▓▓░░░░░░░░░░░░                       │  ← 进度条
├─────────────────────────────────────────────┤
│  Markdown 预览                    1024 字符  │
│  ┌─────────────────────────────────────┐    │
│  │  # 标题                              │    │  ← 结果预览
│  │  正文内容...                         │    │
│  └─────────────────────────────────────┘    │
│              [复制结果] [保存文件] [清空结果] │
└─────────────────────────────────────────────┘
```

## 快速开始

### 方式一：直接使用打包好的 EXE（推荐）

1. 下载 `dist/MarkItDown_Desktop.exe`
2. 双击运行
3. 拖拽文件到窗口或点击「选择文件」
4. 点击「一键转换」

### 方式二：从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

### 打包 EXE

```bash
python build.py
```

打包完成后，`dist/MarkItDown_Desktop.exe` 即为独立可执行文件。

## 功能说明

### 文件转换模式

支持拖拽或点击选择以下格式文件：

| 格式 | 扩展名 |
|------|--------|
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx` |
| 图片 | `.jpg` `.jpeg` `.png` `.gif` `.bmp` |
| 网页 | `.html` `.htm` |
| 数据 | `.csv` `.json` `.xml` |
| 文本 | `.txt` `.md` |
| 压缩包 | `.zip` |

### 文本直转模式

直接粘贴文本内容，选择格式后一键转换：

1. 选择输入格式（HTML / 纯文本 / CSV / JSON / XML / Markdown）
2. 粘贴或输入文本（支持「从剪贴板粘贴」按钮）
3. 点击「一键转换」

## 技术栈

- **GUI 框架**：[PySide6](https://www.qt.io/qt-for-python) (Qt for Python)
- **转换引擎**：[markitdown](https://github.com/microsoft/markitdown) by Microsoft
- **打包工具**：[PyInstaller](https://pyinstaller.org/)
- **线程模型**：QThread + 信号槽，保证 UI 不卡顿

## 项目结构

```
MarkItDown_Desktop/
├── app.py              # 主程序（GUI + 转换逻辑）
├── build.py            # 一键打包脚本
├── requirements.txt    # Python 依赖清单
├── dist/               # 打包输出目录
│   └── MarkItDown_Desktop.exe
└── README.md
```

## 许可证

本项目基于 MIT 许可证。
MarkItDown 由 Microsoft 开源，遵循 MIT 许可证。
