import os
import sys
import subprocess
import traceback

# 修复 Windows 控制台 GBK 编码无法输出 emoji 的问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def install_dependencies():
    print("正在为您安装打包所需的依赖项...")

    # --- 核心打包与 GUI 依赖 ---
    core_deps = [
        "pyinstaller",
        "PySide6",
    ]

    # --- markitdown 本体（不加 [all]，避免拉取 torch/whisper 等多 GB 依赖）---
    # 仅安装轻量级文档格式转换器
    format_deps = [
        "pdfminer.six",
        "python-docx",
        "python-pptx",
        "openpyxl",
        "mammoth",
        "pypdf",
        "pdfplumber",
        "beautifulsoup4",
        "lxml",
        "charset-normalizer",
    ]

    # 先装核心依赖（必须成功）
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install"] + core_deps
    )

    # ---- 关键：强制卸载 markitdown 的 editable 安装，再做普通安装 ----
    # editable 模式安装的包 PyInstaller 无法正确收集，会导致打包后 No module named 'markitdown'
    print("\n正在检查 markitdown 安装方式...")
    subprocess.call(
        [sys.executable, "-m", "pip", "uninstall", "-y", "markitdown"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "markitdown"]
    )

    # 再装格式依赖（允许部分失败，不影响打包流程）
    for dep in format_deps:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep]
            )
        except subprocess.CalledProcessError:
            print(f"  [!] 无法安装 {dep}（可能暂不支持当前 Python 版本），跳过。")

    # --- 卸载之前 markitdown[all] 拉取的重型依赖（如果存在）---
    heavy_pkgs = [
        "torch",
        "torchvision",
        "torchaudio",
        "openai-whisper",
        "whisper",
        "openai",
        "pydub",
        "SpeechRecognition",
        "youtube-transcript-api",
        "yt-dlp",
        "tensorflow",
        "tensorboard",
    ]
    print("\n清理可能存在的重型依赖（torch/whisper 等）...")
    subprocess.call(
        [sys.executable, "-m", "pip", "uninstall", "-y"] + heavy_pkgs,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("依赖安装步骤完成。\n")


def build_exe():
    print("开始使用 PyInstaller 打包 MarkItDown 桌面客户端...")

    # ---------------------------------------------------------------
    # 关键修复：使用 sys.executable -m PyInstaller 而非直接调用
    #           "pyinstaller" 可执行文件，避免 [WinError 2] 找不到文件
    # ---------------------------------------------------------------
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--noconsole",
        "--name=MarkItDown_Desktop",
        "app.py",
    ]

    # ---- 隐藏导入：确保 markitdown 底层各转换器被完整打包 ----
    # 根据 markitdown 0.1.7 实际包结构修正
    hidden_imports = [
        "markitdown",
        "markitdown._markitdown",
        "markitdown._base_converter",
        "markitdown._stream_info",
        "markitdown._uri_utils",
        "markitdown._exceptions",
        "markitdown.__about__",
        "markitdown.converters",
        "markitdown.converters._docx_converter",
        "markitdown.converters._xlsx_converter",
        "markitdown.converters._pptx_converter",
        "markitdown.converters._pdf_converter",
        "markitdown.converters._image_converter",
        "markitdown.converters._html_converter",
        "markitdown.converters._csv_converter",
        "markitdown.converters._zip_converter",
        "markitdown.converters._plain_text_converter",
        "markitdown.converters._ipynb_converter",
        "markitdown.converters._rss_converter",
        "markitdown.converters._epub_converter",
        "markitdown.converters._bing_serp_converter",
        "markitdown.converters._wikipedia_converter",
        "markitdown.converters._outlook_msg_converter",
        "markitdown.converters._markdownify",
        "markitdown.converter_utils",
        "markitdown.converter_utils.docx",
        "markitdown.converter_utils.docx.pre_process",
        "markitdown.converter_utils.docx.math",
        "markitdown.converter_utils.docx.math.latex_dict",
        "markitdown.converter_utils.docx.math.omml",
        "numpy",
        "numpy.core",
        "openpyxl",
        "pptx",
        "docx",
        "pdfplumber",
        "pypdf",
        "pdfminer",
        "pdfminer.high_level",
        "mammoth",
        "bs4",
        "lxml",
        "lxml._elementpath",
        "PIL",
        "PIL.Image",
        "onnxruntime",
        "magika",
        "jinja2",
        "requests",
        "pydantic",
        "defusedxml",
        "markdownify",
        "soupsieve",
        "charset_normalizer",
        "pathlib",
        "tempfile",
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # ---- 排除不需要的重型模块，减小 EXE 体积 ----
    exclude_modules = [
        "torch",
        "torchvision",
        "torchaudio",
        "whisper",
        "openai",
        "pydub",
        "speech_recognition",
        "youtube_transcript_api",
        "yt_dlp",
        "tensorflow",
        "tensorboard",
        "sympy",
        "pygame",
        "pygame_ce",
        "_pytest",
        "pytest",
        "IPython",
        "jupyter",
        "notebook",
        "matplotlib",
        "tkinter",
    ]

    for mod in exclude_modules:
        cmd.extend(["--exclude-module", mod])

    # ---- collect-all：收集数据文件、动态库、子模块 ----
    collect_all_pkgs = [
        "markitdown",
        "markitdown.converters",
        "markitdown.converter_utils",
        "numpy",
        "onnxruntime",
        "magika",
        "openpyxl",
        "pptx",
        "docx",
        "pdfminer",
        "pdfplumber",
        "pypdf",
        "mammoth",
        "bs4",
        "lxml",
        "PIL",
        "defusedxml",
        "markdownify",
        "charset_normalizer",
    ]

    for pkg in collect_all_pkgs:
        cmd.extend(["--collect-all", pkg])

    print(f"执行打包命令 (摘要):\n  {' '.join(cmd[:6])} ...")
    print(f"  共 {len(hidden_imports)} 个 hidden-import")
    print(f"  共 {len(exclude_modules)} 个 exclude-module")
    print(f"  共 {len(collect_all_pkgs)} 个 collect-all\n")

    subprocess.check_call(cmd)

    print("\n" + "=" * 55)
    print("[OK] 恭喜您！打包完成！")
    print("     生成的文件: dist/MarkItDown_Desktop.exe")
    print("     可直接拷贝到任意 Windows 电脑双击运行，无需安装 Python。")
    print("=" * 55)


if __name__ == "__main__":
    try:
        install_dependencies()
        build_exe()
    except Exception as e:
        print(f"\n[ERROR] 打包过程中遇到错误: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
