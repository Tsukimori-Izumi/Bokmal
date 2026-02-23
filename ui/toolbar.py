"""Toolbar - Ribbon-style toolbar for UniTK."""

from PySide6.QtWidgets import (
    QToolBar, QToolButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QFont

from ui.theme import COLORS


class ToolbarGroup(QFrame):
    """A labeled group of toolbar buttons."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ToolbarGroup {{
                border-right: 1px solid {COLORS['border']};
                padding: 0 4px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 0)
        layout.setSpacing(0)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(2)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(self.button_layout)

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 9px;")
        layout.addWidget(label)

    def add_button(self, btn: QToolButton):
        self.button_layout.addWidget(btn)


def _make_button(text: str, icon_text: str = "", tooltip: str = "",
                 checkable: bool = False) -> QToolButton:
    """Create a styled toolbar button."""
    btn = QToolButton()
    if icon_text:
        btn.setText(f"{icon_text} {text}")
    else:
        btn.setText(text)
    btn.setToolTip(tooltip or text)
    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
    btn.setCheckable(checkable)
    btn.setMinimumWidth(32)
    font = QFont("Segoe UI", 11)
    btn.setFont(font)
    return btn


class MainToolbar(QToolBar):
    """Main application toolbar."""

    # Signals
    new_project_clicked = Signal()
    add_task_clicked = Signal()
    delete_task_clicked = Signal()
    indent_clicked = Signal()
    outdent_clicked = Signal()
    link_tasks_clicked = Signal()
    unlink_tasks_clicked = Signal()
    milestone_clicked = Signal()
    task_info_clicked = Signal()
    scroll_today_clicked = Signal()
    undo_clicked = Signal()
    redo_clicked = Signal()
    save_clicked = Signal()
    open_clicked = Signal()
    export_csv_clicked = Signal()
    import_csv_clicked = Signal()
    export_excel_clicked = Signal()
    export_pptx_clicked = Signal()
    set_baseline_clicked = Signal()
    toggle_wbs_clicked = Signal()
    sort_waterfall_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__("メインツールバー", parent)
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.setFixedHeight(58)

        self._build_toolbar()

    def _build_toolbar(self):
        # === File Group ===
        file_group = ToolbarGroup("ファイル")

        self.btn_new = _make_button("新規", "📄", "新規プロジェクトを作成")
        self.btn_new.clicked.connect(self.new_project_clicked.emit)
        file_group.add_button(self.btn_new)

        self.btn_save = _make_button("保存", "💾", "プロジェクトを保存")
        self.btn_save.clicked.connect(self.save_clicked.emit)
        file_group.add_button(self.btn_save)

        self.btn_open = _make_button("開く", "📂", "プロジェクトを開く")
        self.btn_open.clicked.connect(self.open_clicked.emit)
        file_group.add_button(self.btn_open)

        self.addWidget(file_group)
        self.addSeparator()

        # === Edit Group ===
        edit_group = ToolbarGroup("編集")

        self.btn_undo = _make_button("戻す", "↩", "元に戻す (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo_clicked.emit)
        edit_group.add_button(self.btn_undo)

        self.btn_redo = _make_button("やり直", "↪", "やり直し (Ctrl+Y)")
        self.btn_redo.clicked.connect(self.redo_clicked.emit)
        edit_group.add_button(self.btn_redo)

        self.addWidget(edit_group)
        self.addSeparator()

        # === Task Group ===
        task_group = ToolbarGroup("タスク")

        self.btn_add = _make_button("追加", "➕", "新規タスクを追加 (Insert)")
        self.btn_add.clicked.connect(self.add_task_clicked.emit)
        task_group.add_button(self.btn_add)

        self.btn_delete = _make_button("削除", "🗑", "タスクを削除 (Delete)")
        self.btn_delete.clicked.connect(self.delete_task_clicked.emit)
        task_group.add_button(self.btn_delete)

        self.btn_info = _make_button("情報", "ℹ", "タスク情報を表示")
        self.btn_info.clicked.connect(self.task_info_clicked.emit)
        task_group.add_button(self.btn_info)

        self.btn_milestone = _make_button("MS", "◆", "マイルストーン切替")
        self.btn_milestone.clicked.connect(self.milestone_clicked.emit)
        task_group.add_button(self.btn_milestone)

        self.addWidget(task_group)
        self.addSeparator()

        # === View/Sort Group ===
        view_group = ToolbarGroup("表示・整列")
        
        self.btn_toggle_wbs = _make_button("WBS", "◀▶", "WBS表示切替")
        self.btn_toggle_wbs.clicked.connect(self.toggle_wbs_clicked.emit)
        view_group.add_button(self.btn_toggle_wbs)
        
        self.btn_sort_wf = _make_button("WF", "🌊", "ウォーターフォール順に並べ替え")
        self.btn_sort_wf.clicked.connect(self.sort_waterfall_clicked.emit)
        view_group.add_button(self.btn_sort_wf)

        self.addWidget(view_group)
        self.addSeparator()

        # === Structure Group ===
        struct_group = ToolbarGroup("構造")

        self.btn_indent = _make_button("→", "→", "インデント (Tab)")
        self.btn_indent.clicked.connect(self.indent_clicked.emit)
        struct_group.add_button(self.btn_indent)

        self.btn_outdent = _make_button("←", "←", "アウトデント (Shift+Tab)")
        self.btn_outdent.clicked.connect(self.outdent_clicked.emit)
        struct_group.add_button(self.btn_outdent)

        self.btn_link = _make_button("🔗", "🔗", "タスクをリンク")
        self.btn_link.clicked.connect(self.link_tasks_clicked.emit)
        struct_group.add_button(self.btn_link)

        self.btn_unlink = _make_button("✂", "✂", "リンク解除")
        self.btn_unlink.clicked.connect(self.unlink_tasks_clicked.emit)
        struct_group.add_button(self.btn_unlink)

        self.addWidget(struct_group)
        self.addSeparator()

        # === Schedule Group ===
        sched_group = ToolbarGroup("スケジュール")

        self.btn_baseline = _make_button("基準", "📋", "ベースライン設定")
        self.btn_baseline.clicked.connect(self.set_baseline_clicked.emit)
        sched_group.add_button(self.btn_baseline)

        self.btn_today = _make_button("今日", "📅", "今日にスクロール")
        self.btn_today.clicked.connect(self.scroll_today_clicked.emit)
        sched_group.add_button(self.btn_today)

        self.addWidget(sched_group)
        self.addSeparator()

        # === Data Group ===
        data_group = ToolbarGroup("データ")

        self.btn_export = _make_button("CSV", "📤", "CSVエクスポート")
        self.btn_export.clicked.connect(self.export_csv_clicked.emit)
        data_group.add_button(self.btn_export)

        self.btn_export_excel = _make_button("Excel", "📊", "Excel(.xlsx)エクスポート")
        self.btn_export_excel.clicked.connect(self.export_excel_clicked.emit)
        data_group.add_button(self.btn_export_excel)

        self.btn_export_pptx = _make_button("PPT", "📽️", "PowerPoint(.pptx)ガントエクスポート")
        self.btn_export_pptx.clicked.connect(self.export_pptx_clicked.emit)
        data_group.add_button(self.btn_export_pptx)

        self.btn_import = _make_button("読込", "📥", "CSVインポート")
        self.btn_import.clicked.connect(self.import_csv_clicked.emit)
        data_group.add_button(self.btn_import)

        self.addWidget(data_group)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
