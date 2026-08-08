import os
import sys
import tempfile
import traceback
from PySide6.QtCore import (
    Qt, Signal, QObject, QThread, QPropertyAnimation, QEasingCurve,
    QTimer, QSize, QRect, QPoint
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QFrame, QMessageBox, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSplashScreen, QStackedWidget, QComboBox
)
from PySide6.QtGui import (
    QFont, QColor, QDragEnterEvent, QDropEvent, QPainter, QLinearGradient,
    QPen, QBrush, QPixmap, QIcon, QFontDatabase
)

# ============================================================
#  全局异常钩子：--noconsole 模式下防止程序静默崩溃
# ============================================================
def _global_excepthook(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.getcwd()
        with open(os.path.join(base, "markitdown_error.log"), "a", encoding="utf-8") as f:
            f.write(msg + "\n" + "=" * 60 + "\n")
    except Exception:
        pass
    try:
        QMessageBox.critical(None, "程序异常", f"发生未捕获的异常:\n\n{exc_value}\n\n详细信息已写入 markitdown_error.log")
    except Exception:
        pass

sys.excepthook = _global_excepthook


# ============================================================
#  颜色常量 — 现代深色渐变主题
# ============================================================
class C:
    BG          = "#F0F2F5"
    CARD_BG     = "#FFFFFF"
    PRIMARY     = "#4F6AF0"
    PRIMARY_H   = "#3D56D4"
    PRIMARY_D   = "#2E41B8"
    ACCENT      = "#7B5CFA"
    SUCCESS     = "#22C55E"
    DANGER      = "#EF4444"
    WARNING     = "#F59E0B"
    TEXT        = "#1E293B"
    TEXT_SEC    = "#64748B"
    TEXT_MUTE   = "#94A3B8"
    BORDER      = "#E2E8F0"
    BORDER_HL   = "#C7D2FE"
    INPUT_BG    = "#F8FAFC"
    GRAD_TOP    = "#4F6AF0"
    GRAD_BOT    = "#7B5CFA"
    TAB_INACTIVE = "#E2E8F0"
    TAB_ACTIVE_BG = "#FFFFFF"


# ============================================================
#  自定义无边框渐变标题栏
# ============================================================
class GradientHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(68)
        self._title = "MarkItDown"
        self._subtitle = "智能文档转换"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        grad = QLinearGradient(0, 0, rect.width(), 0)
        grad.setColorAt(0.0, QColor(C.GRAD_TOP))
        grad.setColorAt(1.0, QColor(C.GRAD_BOT))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)

        painter.setBrush(QColor(255, 255, 255, 30))
        painter.drawEllipse(QPoint(rect.width() - 120, 20), 60, 60)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawEllipse(QPoint(rect.width() - 40, 50), 40, 40)

        painter.setPen(QColor(255, 255, 255))
        title_font = QFont("Microsoft YaHei", 15, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(QRect(24, 12, 400, 30), Qt.AlignLeft | Qt.AlignVCenter, self._title)

        painter.setPen(QColor(255, 255, 255, 200))
        sub_font = QFont("Microsoft YaHei", 8)
        painter.setFont(sub_font)
        painter.drawText(QRect(24, 38, 400, 22), Qt.AlignLeft | Qt.AlignVCenter, self._subtitle)


# ============================================================
#  Tab 切换器 — 文件转换 / 文本直转
# ============================================================
class TabSwitcher(QWidget):
    tabChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self._current = 0
        self._tabs = ["文件转换", "文本直转"]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)

        self._buttons = []
        for i, name in enumerate(self._tabs):
            btn = QPushButton(name)
            btn.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self._switch(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch()

        self._update_styles()

    def _switch(self, idx):
        if idx == self._current:
            return
        self._current = idx
        self._update_styles()
        self.tabChanged.emit(idx)

    def _update_styles(self):
        for i, btn in enumerate(self._buttons):
            if i == self._current:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {C.PRIMARY};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 0 22px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {C.TAB_INACTIVE};
                        color: {C.TEXT_SEC};
                        border: none;
                        border-radius: 8px;
                        padding: 0 22px;
                    }}
                    QPushButton:hover {{
                        background-color: {C.BORDER};
                        color: {C.TEXT};
                    }}
                """)


# ============================================================
#  现代化按钮
# ============================================================
class ModernButton(QPushButton):
    def __init__(self, text, parent=None, variant="primary"):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
        self.setFixedHeight(38)
        self.setCursor(Qt.PointingHandCursor)
        self._variant = variant
        self._apply_style()

    def _apply_style(self):
        if self._variant == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 20px;
                }}
                QPushButton:hover {{
                    background-color: {C.PRIMARY_H};
                }}
                QPushButton:pressed {{
                    background-color: {C.PRIMARY_D};
                }}
                QPushButton:disabled {{
                    background-color: {C.BORDER};
                    color: {C.TEXT_MUTE};
                }}
            """)
        elif self._variant == "success":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 20px;
                }}
                QPushButton:hover {{
                    background-color: #16A34A;
                }}
                QPushButton:pressed {{
                    background-color: #15803D;
                }}
                QPushButton:disabled {{
                    background-color: {C.BORDER};
                    color: {C.TEXT_MUTE};
                }}
            """)
        else:  # ghost
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {C.TEXT};
                    border: 1.5px solid {C.BORDER};
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {C.INPUT_BG};
                    border-color: {C.PRIMARY};
                    color: {C.PRIMARY};
                }}
                QPushButton:pressed {{
                    background-color: {C.BORDER};
                }}
                QPushButton:disabled {{
                    color: {C.TEXT_MUTE};
                    border-color: {C.BORDER};
                }}
            """)


# ============================================================
#  现代化下拉选择框
# ============================================================
class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setFont(QFont("Microsoft YaHei", 9))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {C.INPUT_BG};
                border: 1.5px solid {C.BORDER};
                border-radius: 8px;
                padding: 0 12px;
                color: {C.TEXT};
            }}
            QComboBox:hover {{
                border-color: {C.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {C.TEXT_SEC};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {C.CARD_BG};
                border: 1px solid {C.BORDER};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {C.PRIMARY};
                selection-color: white;
            }}
        """)


# ============================================================
#  拖拽区 — 现代化大区域 + 动画反馈
# ============================================================
class DragDropArea(QFrame):
    fileDropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(190)
        self._drag_active = False
        self._has_file = False

        self._normal_qss = f"""
            QFrame {{
                border: 2px dashed {C.BORDER};
                border-radius: 16px;
                background-color: {C.INPUT_BG};
            }}
        """
        self._active_qss = f"""
            QFrame {{
                border: 2px dashed {C.PRIMARY};
                border-radius: 16px;
                background-color: #EEF2FF;
            }}
        """
        self._file_qss = f"""
            QFrame {{
                border: 2px solid {C.PRIMARY};
                border-radius: 16px;
                background-color: #F5F3FF;
            }}
        """
        self.setStyleSheet(self._normal_qss)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        self.icon_label = QLabel("📁", self)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 40))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("拖拽文件到此处", self)
        self.title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(f"color: {C.TEXT};")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.hint_label = QLabel("或点击下方按钮选择文件  ·  支持 PDF / Word / PPT / Excel / 图片等", self)
        self.hint_label.setFont(QFont("Microsoft YaHei", 9))
        self.hint_label.setStyleSheet(f"color: {C.TEXT_SEC};")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)
        layout.addStretch()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            if not self._has_file:
                self._drag_active = True
                self.setStyleSheet(self._active_qss)
                self.icon_label.setText("📂")

    def dragLeaveEvent(self, event):
        if not self._has_file:
            self._drag_active = False
            self.setStyleSheet(self._normal_qss)
            self.icon_label.setText("📁")

    def dropEvent(self, event: QDropEvent):
        self._drag_active = False
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.fileDropped.emit(file_path)

    def set_file_loaded(self, filename):
        self._has_file = True
        self.setStyleSheet(self._file_qss)
        self.icon_label.setText("📄")
        self.title_label.setText(filename)
        self.title_label.setStyleSheet(f"color: {C.PRIMARY};")
        self.hint_label.setText("文件已加载，点击「一键转换」开始处理")

    def reset(self):
        self._has_file = False
        self._drag_active = False
        self.setStyleSheet(self._normal_qss)
        self.icon_label.setText("📁")
        self.title_label.setText("拖拽文件到此处")
        self.title_label.setStyleSheet(f"color: {C.TEXT};")
        self.hint_label.setText("或点击下方按钮选择文件  ·  支持 PDF / Word / PPT / Excel / 图片等")


# ============================================================
#  后台转换线程 — 文件转换
# ============================================================
class FileConversionWorker(QObject):
    finished = Signal(bool, str, str)
    progress = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            self.progress.emit("正在初始化转换引擎...")
            from markitdown import MarkItDown
            md = MarkItDown()
            self.progress.emit(f"正在转换: {os.path.basename(self.file_path)}")
            result = md.convert(self.file_path)
            self.finished.emit(True, result.text_content, "")
        except Exception as e:
            self.finished.emit(False, "", str(e))


# ============================================================
#  后台转换线程 — 文本直转
# ============================================================
class TextConversionWorker(QObject):
    finished = Signal(bool, str, str)
    progress = Signal(str)

    # 格式名 → 临时文件后缀
    FORMAT_MAP = {
        "HTML":  ".html",
        "纯文本": ".txt",
        "CSV":   ".csv",
        "JSON":  ".json",
        "XML":   ".xml",
        "Markdown": ".md",
    }

    def __init__(self, text, fmt_name):
        super().__init__()
        self.text = text
        self.fmt_name = fmt_name

    def run(self):
        tmp_path = None
        try:
            self.progress.emit("正在写入临时文件...")
            ext = self.FORMAT_MAP.get(self.fmt_name, ".txt")

            # 写入临时文件
            fd, tmp_path = tempfile.mkstemp(suffix=ext, prefix="markitdown_")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(self.text)

            self.progress.emit(f"正在转换 {self.fmt_name} 文本...")
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(tmp_path)
            self.finished.emit(True, result.text_content, "")
        except Exception as e:
            self.finished.emit(False, "", str(e))
        finally:
            # 清理临时文件
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass


# ============================================================
#  主窗口
# ============================================================
class MarkItDownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_file_path = ""
        self.converted_markdown = ""
        self._worker = None
        self._thread = None
        self._current_tab = 0  # 0=文件转换, 1=文本直转
        self._init_window()
        self._build_ui()
        self._fade_in()

    # ---- 窗口基础 ----
    def _init_window(self):
        self.setWindowTitle("MarkItDown — 极速文档转 Markdown")
        self.resize(900, 720)
        self.setMinimumSize(760, 580)
        self.setStyleSheet(f"QMainWindow {{ background-color: {C.BG}; }}")

    # ---- 淡入动画 ----
    def _fade_in(self):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self._anim = QPropertyAnimation(self.effect, b"opacity", self)
        self._anim.setDuration(300)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    # ---- 构建 UI ----
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # === 渐变标题栏 ===
        self.header = GradientHeader(self)
        root.addWidget(self.header)

        # === 内容区 ===
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 16, 28, 24)
        content_layout.setSpacing(16)

        # --- Tab 切换器 ---
        self.tab_switcher = TabSwitcher(self)
        self.tab_switcher.tabChanged.connect(self._on_tab_changed)
        content_layout.addWidget(self.tab_switcher)

        # --- StackedWidget: 文件转换页 / 文本直转页 ---
        self.stack = QStackedWidget()

        # ---- 页面 0: 文件转换 ----
        page_file = QWidget()
        page_file_layout = QVBoxLayout(page_file)
        page_file_layout.setContentsMargins(0, 0, 0, 0)
        page_file_layout.setSpacing(16)

        self.drop_area = DragDropArea(self)
        self.drop_area.fileDropped.connect(self._on_file)
        page_file_layout.addWidget(self.drop_area)

        # 文件模式按钮行
        file_btn_row = QHBoxLayout()
        file_btn_row.setSpacing(10)
        self.btn_select = ModernButton("选择文件", variant="ghost")
        self.btn_select.clicked.connect(self._select_file)
        self.btn_convert_file = ModernButton("一键转换", variant="primary")
        self.btn_convert_file.clicked.connect(self._start_file_convert)
        self.btn_convert_file.setEnabled(False)
        self.btn_clear_file = ModernButton("清除选择", variant="ghost")
        self.btn_clear_file.clicked.connect(self._clear_file)
        self.btn_clear_file.setEnabled(False)
        file_btn_row.addWidget(self.btn_select)
        file_btn_row.addWidget(self.btn_convert_file)
        file_btn_row.addWidget(self.btn_clear_file)
        file_btn_row.addStretch()
        page_file_layout.addLayout(file_btn_row)

        self.stack.addWidget(page_file)

        # ---- 页面 1: 文本直转 ----
        page_text = QWidget()
        page_text_layout = QVBoxLayout(page_text)
        page_text_layout.setContentsMargins(0, 0, 0, 0)
        page_text_layout.setSpacing(12)

        # 格式选择行
        fmt_row = QHBoxLayout()
        fmt_label = QLabel("输入格式:")
        fmt_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
        fmt_label.setStyleSheet(f"color: {C.TEXT};")
        fmt_row.addWidget(fmt_label)

        self.combo_format = ModernComboBox()
        self.combo_format.addItems(["HTML", "纯文本", "CSV", "JSON", "XML", "Markdown"])
        fmt_row.addWidget(self.combo_format)

        # 粘贴按钮
        self.btn_paste = ModernButton("从剪贴板粘贴", variant="ghost")
        self.btn_paste.clicked.connect(self._paste_clipboard)
        fmt_row.addStretch()
        fmt_row.addWidget(self.btn_paste)

        page_text_layout.addLayout(fmt_row)

        # 文本输入区
        input_header = QHBoxLayout()
        input_title = QLabel("输入原始文本")
        input_title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.DemiBold))
        input_title.setStyleSheet(f"color: {C.TEXT};")
        input_header.addWidget(input_title)
        input_header.addStretch()
        self.input_char_count = QLabel("0 字符")
        self.input_char_count.setFont(QFont("Microsoft YaHei", 8))
        self.input_char_count.setStyleSheet(f"color: {C.TEXT_MUTE};")
        input_header.addWidget(self.input_char_count)
        page_text_layout.addLayout(input_header)

        self.text_input = QTextEdit()
        self.text_input.setFont(QFont("Consolas", 10))
        self.text_input.setPlaceholderText("在此粘贴或输入原始文本内容...\n\n例如：\n  • 粘贴一段 HTML 网页代码，选择「HTML」格式\n  • 粘贴 CSV 数据，选择「CSV」格式\n  • 粘贴 JSON 数据，选择「JSON」格式\n\n选择对应格式后点击「一键转换」即可得到干净的 Markdown。")
        self.text_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C.CARD_BG};
                border: 1px solid {C.BORDER};
                border-radius: 12px;
                padding: 14px;
                color: {C.TEXT};
                selection-background-color: {C.BORDER_HL};
            }}
        """)
        self.text_input.textChanged.connect(self._on_text_input_changed)
        page_text_layout.addWidget(self.text_input, 1)

        # 文本模式转换按钮
        text_btn_row = QHBoxLayout()
        text_btn_row.setSpacing(10)
        self.btn_convert_text = ModernButton("一键转换", variant="primary")
        self.btn_convert_text.clicked.connect(self._start_text_convert)
        self.btn_convert_text.setEnabled(False)
        self.btn_clear_text = ModernButton("清空输入", variant="ghost")
        self.btn_clear_text.clicked.connect(self._clear_text_input)
        text_btn_row.addWidget(self.btn_convert_text)
        text_btn_row.addWidget(self.btn_clear_text)
        text_btn_row.addStretch()
        page_text_layout.addLayout(text_btn_row)

        self.stack.addWidget(page_text)

        content_layout.addWidget(self.stack, 1)

        # --- 公共：状态条 + 进度条 ---
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Microsoft YaHei", 9))
        self.status_dot.setStyleSheet(f"color: {C.TEXT_MUTE};")
        self.status_dot.setFixedWidth(16)

        self.status_label = QLabel("准备就绪")
        self.status_label.setFont(QFont("Microsoft YaHei", 9))
        self.status_label.setStyleSheet(f"color: {C.TEXT_SEC};")

        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        content_layout.addLayout(status_row)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {C.BORDER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {C.PRIMARY};
                border-radius: 2px;
            }}
        """)
        content_layout.addWidget(self.progress)

        # --- 结果预览区 ---
        preview_header = QHBoxLayout()
        preview_title = QLabel("Markdown 预览")
        preview_title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.DemiBold))
        preview_title.setStyleSheet(f"color: {C.TEXT};")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()

        self.char_count = QLabel("0 字符")
        self.char_count.setFont(QFont("Microsoft YaHei", 8))
        self.char_count.setStyleSheet(f"color: {C.TEXT_MUTE};")
        preview_header.addWidget(self.char_count)
        content_layout.addLayout(preview_header)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Consolas", 10))
        self.preview.setPlaceholderText("转换结果将在此处实时展示...")
        self.preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C.CARD_BG};
                border: 1px solid {C.BORDER};
                border-radius: 12px;
                padding: 14px;
                color: {C.TEXT};
                selection-background-color: {C.BORDER_HL};
            }}
        """)
        content_layout.addWidget(self.preview, 1)

        # --- 底部操作按钮 ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        self.btn_save = ModernButton("保存文件", variant="success")
        self.btn_save.clicked.connect(self._save_file)
        self.btn_save.setEnabled(False)

        self.btn_copy = ModernButton("复制结果", variant="ghost")
        self.btn_copy.clicked.connect(self._copy)
        self.btn_copy.setEnabled(False)

        self.btn_clear_result = ModernButton("清空结果", variant="ghost")
        self.btn_clear_result.clicked.connect(self._clear_result)

        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_copy)
        bottom_row.addWidget(self.btn_save)
        bottom_row.addWidget(self.btn_clear_result)
        content_layout.addLayout(bottom_row)

        root.addWidget(content, 1)

    # ============================================================
    #  Tab 切换
    # ============================================================
    def _on_tab_changed(self, idx):
        self._current_tab = idx
        self.stack.setCurrentIndex(idx)
        self._reset_state()
        if idx == 0:
            self._set_status("文件转换模式 · 准备就绪")
        else:
            self._set_status("文本直转模式 · 粘贴或输入文本后点击转换")

    # ============================================================
    #  状态管理
    # ============================================================
    def _set_status(self, text, color=C.TEXT_SEC):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_dot.setStyleSheet(f"color: {color};")

    # ============================================================
    #  文件模式：选择 / 拖拽
    # ============================================================
    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择要转换的文档", "",
            "所有支持的文件 (*.pdf *.docx *.xlsx *.pptx *.html *.htm *.jpg *.jpeg *.png *.gif *.bmp *.csv *.json *.xml *.txt *.md *.zip);;"
            "PDF 文档 (*.pdf);;Office 文档 (*.docx *.xlsx *.pptx);;图片文件 (*.jpg *.jpeg *.png *.gif *.bmp);;"
            "网页文件 (*.html *.htm);;所有文件 (*.*)"
        )
        if path:
            self._on_file(path)

    def _on_file(self, path):
        self.selected_file_path = path
        name = os.path.basename(path)
        self.drop_area.set_file_loaded(name)
        self._set_status(f"已加载: {name}", C.PRIMARY)
        self.btn_convert_file.setEnabled(True)
        self.btn_clear_file.setEnabled(True)
        self._clear_result()

    def _clear_file(self):
        """清除已选择的文件"""
        self.selected_file_path = ""
        self.drop_area.reset()
        self.btn_convert_file.setEnabled(False)
        self.btn_clear_file.setEnabled(False)
        self._set_status("已清除文件选择")

    def _start_file_convert(self):
        if not self.selected_file_path:
            return
        self._set_converting(True)
        self._set_status("正在转换...", C.WARNING)

        self._worker = FileConversionWorker(self.selected_file_path)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    # ============================================================
    #  文本模式：输入 / 粘贴 / 转换
    # ============================================================
    def _on_text_input_changed(self):
        text = self.text_input.toPlainText()
        count = len(text)
        self.input_char_count.setText(f"{count} 字符")
        self.btn_convert_text.setEnabled(count > 0)

    def _paste_clipboard(self):
        clip = QApplication.clipboard()
        text = clip.text()
        if text:
            self.text_input.setPlainText(text)
            self._set_status("已从剪贴板粘贴文本", C.PRIMARY)
        else:
            self._set_status("剪贴板中没有文本内容", C.WARNING)

    def _clear_text_input(self):
        self.text_input.clear()
        self.input_char_count.setText("0 字符")
        self.btn_convert_text.setEnabled(False)
        self._set_status("输入已清空")

    def _start_text_convert(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        fmt = self.combo_format.currentText()
        self._set_converting(True)
        self._set_status(f"正在转换 {fmt} 文本...", C.WARNING)

        self._worker = TextConversionWorker(text, fmt)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    # ============================================================
    #  转换完成回调（两种模式共用）
    # ============================================================
    def _set_converting(self, on):
        self.progress.setRange(0, 0 if on else 100)
        if on:
            self.progress.setValue(0)
        # 禁用/恢复按钮
        self.btn_convert_file.setEnabled(bool(not on and self.selected_file_path))
        self.btn_convert_text.setEnabled(bool(not on and len(self.text_input.toPlainText()) > 0))
        self.btn_select.setEnabled(not on)
        self.btn_clear_file.setEnabled(bool(not on and self.selected_file_path))
        self.btn_paste.setEnabled(not on)
        self.btn_clear_text.setEnabled(not on)
        self.btn_save.setEnabled(bool(not on and self.converted_markdown))
        self.btn_copy.setEnabled(bool(not on and self.converted_markdown))

    def _on_progress(self, msg):
        self._set_status(msg, C.WARNING)

    def _on_finished(self, success, text, error):
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self._set_converting(False)

        if success:
            self.converted_markdown = text
            self.preview.setPlainText(text)
            self.char_count.setText(f"{len(text)} 字符")
            self._set_status("转换完成", C.SUCCESS)
            self.btn_save.setEnabled(True)
            self.btn_copy.setEnabled(True)
            QTimer.singleShot(200, lambda: self._toast("转换成功"))
        else:
            self._set_status("转换失败", C.DANGER)
            QMessageBox.critical(self, "转换失败", f"错误详情:\n{error}")

        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
            self._worker = None

    # ============================================================
    #  保存 / 复制 / 清空
    # ============================================================
    def _save_file(self):
        if not self.converted_markdown:
            return
        if self._current_tab == 0 and self.selected_file_path:
            default_name = os.path.splitext(os.path.basename(self.selected_file_path))[0] + ".md"
        else:
            default_name = "文本转换结果.md"
        path, _ = QFileDialog.getSaveFileName(
            self, "保存 Markdown 文件", default_name,
            "Markdown 文件 (*.md);;文本文件 (*.txt)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.converted_markdown)
                self._toast("文件已保存")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"无法保存文件:\n{e}")

    def _copy(self):
        if self.converted_markdown:
            QApplication.clipboard().setText(self.converted_markdown)
            self._set_status("已复制到剪贴板", C.SUCCESS)
            self._toast("已复制到剪贴板")

    def _clear_result(self):
        self.converted_markdown = ""
        self.preview.clear()
        self.char_count.setText("0 字符")
        self.progress.setValue(0)
        self.btn_save.setEnabled(False)
        self.btn_copy.setEnabled(False)

    def _reset_state(self):
        """切换 Tab 时重置状态"""
        self.selected_file_path = ""
        self.converted_markdown = ""
        self.drop_area.reset()
        self.preview.clear()
        self.char_count.setText("0 字符")
        self.progress.setValue(0)
        self.btn_convert_file.setEnabled(False)
        self.btn_clear_file.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_copy.setEnabled(False)

    # ============================================================
    #  Toast 提示
    # ============================================================
    def _toast(self, message):
        toast = QLabel(message, self)
        toast.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
        toast.setStyleSheet(f"""
            QLabel {{
                background-color: {C.TEXT};
                color: white;
                padding: 10px 24px;
                border-radius: 20px;
            }}
        """)
        toast.adjustSize()
        toast.setAlignment(Qt.AlignCenter)
        x = (self.width() - toast.width()) // 2
        y = self.height() - 100
        toast.move(x, y)
        toast.show()
        toast.raise_()

        eff = QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", toast)
        anim.setDuration(1800)
        anim.setStartValue(0.0)
        anim.setKeyValueAt(0.15, 1.0)
        anim.setKeyValueAt(0.75, 1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(toast.deleteLater)
        anim.start()
        self._toast_anim = anim


# ============================================================
#  启动入口
# ============================================================
def _create_splash():
    pix = QPixmap(360, 180)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    grad = QLinearGradient(0, 0, 360, 180)
    grad.setColorAt(0.0, QColor(C.GRAD_TOP))
    grad.setColorAt(1.0, QColor(C.GRAD_BOT))
    p.setBrush(QBrush(grad))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(0, 0, 360, 180, 16, 16)

    p.setPen(QColor(255, 255, 255))
    p.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
    p.drawText(QRect(0, 35, 360, 40), Qt.AlignCenter, "MarkItDown")

    p.setPen(QColor(255, 255, 255, 200))
    p.setFont(QFont("Microsoft YaHei", 9))
    p.drawText(QRect(0, 78, 360, 25), Qt.AlignCenter, "微软开源 AI 文档预处理神器")
    p.drawText(QRect(0, 105, 360, 25), Qt.AlignCenter, "正在加载...")

    p.end()
    return pix


if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = QSplashScreen(_create_splash())
    splash.show()
    app.processEvents()

    QFontDatabase()

    window = MarkItDownApp()
    QTimer.singleShot(400, lambda: (splash.finish(window), window.show()))
    app.processEvents()

    sys.exit(app.exec())
