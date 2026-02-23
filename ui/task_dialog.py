"""Task Detail Dialog - Edit all task properties."""

from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit,
    QComboBox, QCheckBox, QTextEdit, QPushButton, QLabel,
    QGroupBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate, Signal

from ui.theme import COLORS


class TaskDialog(QDialog):
    """Dialog for editing task properties."""

    task_updated = Signal(dict)

    def __init__(self, task_data: dict | None = None, parent=None):
        super().__init__(parent)
        self.task_data = task_data or {}
        self.setWindowTitle("タスク情報" if task_data else "新規タスク")
        self.setMinimumSize(500, 450)
        self.setModal(True)

        self._build_ui()
        if task_data:
            self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Tab widget
        tabs = QTabWidget()

        # === General Tab ===
        general_tab = QWidget()
        g_layout = QFormLayout(general_tab)
        g_layout.setSpacing(8)
        g_layout.setContentsMargins(16, 16, 16, 16)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("タスク名を入力")
        g_layout.addRow("タスク名:", self.name_edit)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 9999)
        self.duration_spin.setSuffix(" 日")
        g_layout.addRow("期間:", self.duration_spin)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy/MM/dd")
        g_layout.addRow("開始日:", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy/MM/dd")
        g_layout.addRow("終了日:", self.end_date_edit)

        # Actual dates
        self.actual_start_edit = QDateEdit()
        self.actual_start_edit.setCalendarPopup(True)
        self.actual_start_edit.setDisplayFormat("yyyy/MM/dd")
        self.actual_start_edit.setSpecialValueText(" ")
        g_layout.addRow("実績開始日:", self.actual_start_edit)

        self.actual_end_edit = QDateEdit()
        self.actual_end_edit.setCalendarPopup(True)
        self.actual_end_edit.setDisplayFormat("yyyy/MM/dd")
        self.actual_end_edit.setSpecialValueText(" ")
        g_layout.addRow("実績終了日:", self.actual_end_edit)

        self.progress_spin = QDoubleSpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.setSuffix(" %")
        self.progress_spin.setDecimals(0)
        g_layout.addRow("進捗率:", self.progress_spin)

        self.milestone_check = QCheckBox("マイルストーンとして設定")
        g_layout.addRow("", self.milestone_check)

        self.milestone_check.toggled.connect(self._on_milestone_toggled)

        tabs.addTab(general_tab, "一般")

        # === Predecessors Tab ===
        pred_tab = QWidget()
        p_layout = QFormLayout(pred_tab)
        p_layout.setSpacing(8)
        p_layout.setContentsMargins(16, 16, 16, 16)

        self.predecessors_edit = QLineEdit()
        self.predecessors_edit.setPlaceholderText("例: 1FS, 2SS+1d, 3FF-2d")
        p_layout.addRow("先行タスク:", self.predecessors_edit)

        info = QLabel("書式: タスクID + 種別(FS/SS/FF/SF) + ラグ\n"
                       "例: 1FS (タスク1の終了後に開始)\n"
                       "    2SS+2d (タスク2の開始から2日後に開始)\n"
                       "    3FF-1d (タスク3の終了の1日前に終了)")
        info.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        info.setWordWrap(True)
        p_layout.addRow("", info)

        # Constraint
        self.constraint_combo = QComboBox()
        self.constraint_combo.addItem("制約なし", None)
        self.constraint_combo.addItem("指定日以降に開始 (SNET)", "SNET")
        self.constraint_combo.addItem("指定日に開始 (MSO)", "MSO")
        self.constraint_combo.addItem("指定日以前に終了 (FNET)", "FNET")
        self.constraint_combo.addItem("指定日に終了 (MFO)", "MFO")
        p_layout.addRow("制約:", self.constraint_combo)

        self.constraint_date_edit = QDateEdit()
        self.constraint_date_edit.setCalendarPopup(True)
        self.constraint_date_edit.setDisplayFormat("yyyy/MM/dd")
        p_layout.addRow("制約日:", self.constraint_date_edit)

        tabs.addTab(pred_tab, "依存関係")

        # === Notes Tab ===
        notes_tab = QWidget()
        n_layout = QVBoxLayout(notes_tab)
        n_layout.setContentsMargins(16, 16, 16, 16)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("メモを入力...")
        n_layout.addWidget(self.notes_edit)

        tabs.addTab(notes_tab, "メモ")

        layout.addWidget(tabs)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        ok_btn = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText("OK")
        ok_btn.setProperty("primary", True)
        cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setText("キャンセル")
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_milestone_toggled(self, checked):
        if checked:
            self.duration_spin.setValue(0)
            self.duration_spin.setEnabled(False)
        else:
            self.duration_spin.setEnabled(True)
            if self.duration_spin.value() == 0:
                self.duration_spin.setValue(1)

    def _load_data(self):
        t = self.task_data
        self.name_edit.setText(t.get("name", ""))
        self.duration_spin.setValue(t.get("duration", 1))
        self.progress_spin.setValue(t.get("progress", 0))
        self.milestone_check.setChecked(t.get("is_milestone", False))
        self.cost_spin.setValue(t.get("cost", 0))
        self.notes_edit.setPlainText(t.get("notes", "") or "")
        self.predecessors_edit.setText(t.get("predecessors", ""))

        start = t.get("start_date")
        if isinstance(start, date):
            self.start_date_edit.setDate(QDate(start.year, start.month, start.day))
        else:
            self.start_date_edit.setDate(QDate.currentDate())

        end = t.get("end_date")
        if isinstance(end, date):
            self.end_date_edit.setDate(QDate(end.year, end.month, end.day))
        else:
            self.end_date_edit.setDate(QDate.currentDate())

        act_start = t.get("actual_start")
        if isinstance(act_start, date):
            self.actual_start_edit.setDate(QDate(act_start.year, act_start.month, act_start.day))
        else:
            self.actual_start_edit.setDate(self.actual_start_edit.minimumDate())

        act_end = t.get("actual_end")
        if isinstance(act_end, date):
            self.actual_end_edit.setDate(QDate(act_end.year, act_end.month, act_end.day))
        else:
            self.actual_end_edit.setDate(self.actual_end_edit.minimumDate())

        ct = t.get("constraint_type")
        if ct:
            idx = self.constraint_combo.findData(ct)
            if idx >= 0:
                self.constraint_combo.setCurrentIndex(idx)
        cd = t.get("constraint_date")
        if isinstance(cd, date):
            self.constraint_date_edit.setDate(QDate(cd.year, cd.month, cd.day))

    def _on_accept(self):
        qd_start = self.start_date_edit.date()
        qd_end = self.end_date_edit.date()
        qd_constraint = self.constraint_date_edit.date()
        qd_act_start = self.actual_start_edit.date()
        qd_act_end = self.actual_end_edit.date()

        # Actual dates: None if at minimum (empty)
        actual_start = None
        if qd_act_start > self.actual_start_edit.minimumDate():
            actual_start = date(qd_act_start.year(), qd_act_start.month(), qd_act_start.day())

        actual_end = None
        if qd_act_end > self.actual_end_edit.minimumDate():
            actual_end = date(qd_act_end.year(), qd_act_end.month(), qd_act_end.day())

        result = {
            "name": self.name_edit.text() or "New Task",
            "duration": self.duration_spin.value(),
            "start_date": date(qd_start.year(), qd_start.month(), qd_start.day()),
            "end_date": date(qd_end.year(), qd_end.month(), qd_end.day()),
            "actual_start": actual_start,
            "actual_end": actual_end,
            "progress": self.progress_spin.value(),
            "is_milestone": self.milestone_check.isChecked(),
            "cost": self.cost_spin.value(),
            "notes": self.notes_edit.toPlainText(),
            "predecessors": self.predecessors_edit.text(),
            "constraint_type": self.constraint_combo.currentData(),
            "constraint_date": date(qd_constraint.year(), qd_constraint.month(), qd_constraint.day()),
        }

        # Merge with existing data
        self.task_data.update(result)
        self.task_updated.emit(self.task_data)
        self.accept()

    def get_result(self) -> dict:
        return self.task_data
