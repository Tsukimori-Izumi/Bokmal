"""Main Window - Application shell with toolbar, split view, and status bar."""

from datetime import date, timedelta
import copy
import re

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QStatusBar,
    QMessageBox, QFileDialog, QStackedWidget, QLabel, QMenuBar, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut

from ui.toolbar import MainToolbar
from ui.task_table import TaskTableView
from ui.gantt_widget import GanttWidget
from ui.task_dialog import TaskDialog
from ui.resource_sheet import ResourceSheetView
from ui.network_chart import NetworkWidget
from ui.burndown_chart import BurndownWidget

from ui.theme import COLORS
from utils.sample_data import create_sample_project
from utils.export_import import tasks_to_csv, csv_to_tasks, project_to_json, json_to_project, export_tasks_to_excel
from utils.pptx_export import export_gantt_to_pptx
from engine.wbs import WBSManager

from config import APP_TITLE, SPLITTER_DEFAULT_RATIO, GANTT_HEADER_HEIGHT, GANTT_ROW_HEIGHT


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1200, 700)
        self.resize(1400, 850)

        # State
        self._tasks: list[dict] = []
        self._dependencies: list[dict] = []
        self._resources: list[dict] = []
        self._project: dict = {}
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._clipboard: list[dict] = []  # cut/copy buffer
        self._next_task_id: int = 1
        self._current_view: str = "gantt"  # gantt | resources
        self._current_file: str | None = None

        # Auto backup timer (5 minutes)
        self._backup_timer = QTimer(self)
        self._backup_timer.setInterval(300000)
        self._backup_timer.timeout.connect(self._auto_backup)
        self._backup_timer.start()

        self._build_menu_bar()
        self._build_ui()
        self._connect_signals()
        self._load_sample_data()

    def _build_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("ファイル(&F)")

        new_action = QAction("新規プロジェクト(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("開く(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        save_action = QAction("保存(&S)...", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_csv = QAction("CSVエクスポート...", self)
        export_csv.triggered.connect(self._on_export_csv)
        file_menu.addAction(export_csv)

        import_csv = QAction("CSVインポート...", self)
        import_csv.triggered.connect(self._on_import_csv)
        file_menu.addAction(import_csv)

        export_pptx = QAction("PowerPointエクスポート...", self)
        export_pptx.triggered.connect(self._on_export_pptx)
        file_menu.addAction(export_pptx)

        file_menu.addSeparator()

        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("編集(&E)")

        undo_action = QAction("元に戻す(&Z)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("やり直し(&Y)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_action)

        # View menu
        view_menu = menubar.addMenu("表示(&V)")

        gantt_view = QAction("ガントチャート(&G)", self)
        gantt_view.triggered.connect(lambda: self._switch_view("gantt"))
        view_menu.addAction(gantt_view)

        resource_view = QAction("リソースシート(&R)", self)
        resource_view.triggered.connect(lambda: self._switch_view("resources"))
        view_menu.addAction(resource_view)

        network_view = QAction("ネットワークチャート(&N)", self)
        network_view.triggered.connect(lambda: self._switch_view("network"))
        view_menu.addAction(network_view)

        # Task menu
        task_menu = menubar.addMenu("タスク(&T)")

        add_action = QAction("タスク追加(&A)", self)
        add_action.setShortcut(Qt.Key.Key_Insert)
        add_action.triggered.connect(self._on_add_task)
        task_menu.addAction(add_action)

        del_action = QAction("タスク削除(&D)", self)
        del_action.setShortcut(QKeySequence.StandardKey.Delete)
        del_action.triggered.connect(self._on_delete_task)
        task_menu.addAction(del_action)

        task_menu.addSeparator()

        cut_action = QAction("カット(&X)", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._on_cut_task)
        task_menu.addAction(cut_action)

        paste_action = QAction("ペースト(&V)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._on_paste_task)
        task_menu.addAction(paste_action)

        task_menu.addSeparator()

        indent_action = QAction("インデント", self)
        indent_action.setShortcut(Qt.Key.Key_Tab)
        indent_action.triggered.connect(self._on_indent)
        task_menu.addAction(indent_action)

        outdent_action = QAction("アウトデント", self)
        outdent_action.setShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Tab))
        outdent_action.triggered.connect(self._on_outdent)
        task_menu.addAction(outdent_action)

        task_menu.addSeparator()

        info_action = QAction("タスク情報(&I)", self)
        info_action.triggered.connect(self._on_task_info)
        task_menu.addAction(info_action)

        # Help menu
        help_menu = menubar.addMenu("ヘルプ(&H)")

        about_action = QAction("Bokmålについて(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = MainToolbar(self)
        self.addToolBar(self.toolbar)

        # Stacked widget for views
        self.view_stack = QStackedWidget()

        # === Gantt View (Splitter) ===
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setHandleWidth(8)

        # Task table
        self.task_table = TaskTableView()
        self.splitter.addWidget(self.task_table)

        # Right panel: Tabbed (Gantt + Network)
        self.right_tabs = QTabWidget()
        self.right_tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.gantt = GanttWidget()
        self.right_tabs.addTab(self.gantt, "📅 ガントチャート")

        self.network_chart = NetworkWidget()
        self.right_tabs.addTab(self.network_chart, "📊 ネットワーク")

        self.burndown = BurndownWidget()
        self.right_tabs.addTab(self.burndown, "📉 バーンダウン")

        self.splitter.addWidget(self.right_tabs)

        self.splitter.setSizes(SPLITTER_DEFAULT_RATIO)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.view_stack.addWidget(self.splitter)

        # === Resource Sheet View ===
        self.resource_sheet = ResourceSheetView()
        self.resource_sheet.resource_added.connect(self._on_resource_added)
        self.resource_sheet.resource_updated.connect(self._on_resource_updated)
        self.view_stack.addWidget(self.resource_sheet)

        layout.addWidget(self.view_stack)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

        # Sync vertical scroll between table and gantt
        table_vscroll = self.task_table.verticalScrollBar()
        table_vscroll.valueChanged.connect(self._sync_table_gantt_scroll)

    def _connect_signals(self):
        tb = self.toolbar
        tb.new_project_clicked.connect(self._on_new_project)
        tb.add_task_clicked.connect(self._on_add_task)
        tb.delete_task_clicked.connect(self._on_delete_task)
        tb.indent_clicked.connect(self._on_indent)
        tb.outdent_clicked.connect(self._on_outdent)
        tb.link_tasks_clicked.connect(self._on_link_tasks)
        tb.unlink_tasks_clicked.connect(self._on_unlink_tasks)
        tb.milestone_clicked.connect(self._on_toggle_milestone)
        tb.task_info_clicked.connect(self._on_task_info)
        tb.scroll_today_clicked.connect(self._on_scroll_today)
        tb.undo_clicked.connect(self._on_undo)
        tb.redo_clicked.connect(self._on_redo)
        tb.save_clicked.connect(self._on_save)
        tb.open_clicked.connect(self._on_open)
        tb.export_csv_clicked.connect(self._on_export_csv)
        tb.export_excel_clicked.connect(self._on_export_excel)
        tb.export_pptx_clicked.connect(self._on_export_pptx)
        tb.import_csv_clicked.connect(self._on_import_csv)
        tb.set_baseline_clicked.connect(self._on_set_baseline)
        tb.toggle_wbs_clicked.connect(self._on_toggle_wbs)
        tb.sort_waterfall_clicked.connect(self._on_sort_waterfall)

        self.task_table.task_data_changed.connect(self._on_task_data_changed)
        self.task_table.task_moved.connect(self._on_task_moved)
        self.network_chart.dependency_drawn.connect(self._on_dependency_drawn)
        self.gantt.task_date_changed.connect(self._on_gantt_task_date_changed)

    def _load_sample_data(self):
        data = create_sample_project()
        self._project = data["project"]
        self._tasks = data["tasks"]
        self._dependencies = data["dependencies"]
        self._resources = data["resources"]
        self._next_task_id = max(t["id"] for t in self._tasks) + 1 if self._tasks else 1
        self._refresh_views()

    def _save_state(self):
        """Save current state for undo."""
        state = {
            "tasks": copy.deepcopy(self._tasks),
            "dependencies": copy.deepcopy(self._dependencies),
        }
        self._undo_stack.append(state)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _refresh_views(self):
        """Reload all views with current data."""
        self._sync_predecessors_to_tasks()
        self.task_table.load_tasks(self._tasks)
        self.gantt.load_tasks(self._tasks, self._dependencies)
        self.resource_sheet.load_resources(self._resources)
        self.network_chart.load_tasks(self._tasks, self._dependencies)
        self.burndown.load_tasks(self._tasks)
        self._update_status_bar()

    def _update_status_bar(self):
        total = len(self._tasks)
        summary = sum(1 for t in self._tasks if t.get("is_summary"))
        milestones = sum(1 for t in self._tasks if t.get("is_milestone"))
        critical = sum(1 for t in self._tasks if t.get("is_critical") and not t.get("is_summary"))
        self.status_bar.showMessage(
            f"タスク: {total} | サマリー: {summary} | "
            f"マイルストーン: {milestones} | クリティカル: {critical} | "
            f"リソース: {len(self._resources)}"
        )

    def _switch_view(self, view: str):
        if view == "gantt":
            self.view_stack.setCurrentIndex(0)
            self.right_tabs.setCurrentIndex(0)
        elif view == "resources":
            self.view_stack.setCurrentIndex(1)
        elif view == "network":
            self.view_stack.setCurrentIndex(0)
            self.right_tabs.setCurrentIndex(1)
        self._current_view = view

    def resizeEvent(self, event):
        """Re-sync scroll on resize/maximize."""
        super().resizeEvent(event)
        # Re-sync table-gantt scroll after layout change
        QTimer.singleShot(50, self._resync_after_resize)

    def _resync_after_resize(self):
        """Re-apply scroll sync after resize completes."""
        value = self.task_table.verticalScrollBar().value()
        self._sync_table_gantt_scroll(value)

    def _sync_table_gantt_scroll(self, value):
        """Sync table vertical scroll to gantt, accounting for header offset."""
        chart_view = self.gantt.chart
        # Table header is a separate QHeaderView widget, not part of the scroll content.
        # Gantt has a toolbar (32px) + tab bar above it, and the scene header (50px)
        # at the top of the scrollable scene. We need to offset the gantt scroll
        # so that row 0 in both views aligns.
        # When table scrollbar = 0, the gantt should show from scene y = 0
        # (scene header visible, then row 0).
        # The pixel alignment depends on actual widget heights.
        table_header_h = self.task_table.header().height()
        gantt_toolbar_h = 32
        tab_bar_h = self.right_tabs.tabBar().height() if self.right_tabs.tabBar().isVisible() else 0
        # Scene header height that appears above the first task row
        scene_header_in_viewport = GANTT_HEADER_HEIGHT
        # Total height above gantt first task row = tab_bar + toolbar + scene_header
        gantt_header_total = tab_bar_h + gantt_toolbar_h + scene_header_in_viewport
        # Offset: difference between table header and gantt header total
        offset = gantt_header_total - table_header_h
        # Map table scroll to gantt scroll
        chart_view.verticalScrollBar().setValue(value + offset)

    # ========== Task Operations ==========

    def _on_add_task(self):
        self._save_state()
        selected = self.task_table.get_selected_task_indices()
        insert_at = selected[-1] + 1 if selected else len(self._tasks)

        # Determine WBS level from context
        wbs_level = 0
        if insert_at > 0 and insert_at <= len(self._tasks):
            prev = self._tasks[insert_at - 1]
            wbs_level = prev.get("wbs_level", 0)
            if prev.get("is_summary"):
                wbs_level = prev.get("wbs_level", 0) + 1

        today = date.today()
        new_task = {
            "id": self._next_task_id,
            "name": "新規タスク",
            "duration": 5,
            "start_date": today,
            "end_date": today + timedelta(days=6),
            "progress": 0,
            "wbs_level": wbs_level,
            "wbs": "",
            "is_summary": False,
            "is_milestone": False,
            "is_critical": False,
            "parent_id": None,
            "sort_order": insert_at,
            "cost": 0,
            "notes": "",
            "predecessors": "",
            "resource_names": "",
            "constraint_type": None,
            "constraint_date": None,
            "manual_scheduling": False,
            "baseline_start": None,
            "baseline_end": None,
            "baseline_duration": None,
            "actual_start": None,
            "actual_end": None,
        }
        self._next_task_id += 1
        self._tasks.insert(insert_at, new_task)
        self._recalculate_wbs()
        self._refresh_views()

    def _on_delete_task(self):
        indices = self.task_table.get_selected_task_indices()
        if not indices:
            return
        self._save_state()

        # Delete from end to preserve indices
        for idx in reversed(indices):
            if 0 <= idx < len(self._tasks):
                deleted_id = self._tasks[idx]["id"]
                self._tasks.pop(idx)
                # Also remove dependencies involving this task
                self._dependencies = [
                    d for d in self._dependencies
                    if d["predecessor_id"] != deleted_id and d["successor_id"] != deleted_id
                ]

        self._recalculate_wbs()
        self._refresh_views()

    def _on_indent(self):
        indices = self.task_table.get_selected_task_indices()
        if not indices:
            return
        self._save_state()

        # Use WBSManager
        task_objs = _wrap_tasks(self._tasks)
        for idx in indices:
            WBSManager.indent_task(task_objs, idx)
        _unwrap_tasks(task_objs, self._tasks)
        self._recalculate_wbs()
        self._refresh_views()

    def _on_outdent(self):
        indices = self.task_table.get_selected_task_indices()
        if not indices:
            return
        self._save_state()

        task_objs = _wrap_tasks(self._tasks)
        for idx in indices:
            WBSManager.outdent_task(task_objs, idx)
        _unwrap_tasks(task_objs, self._tasks)
        self._recalculate_wbs()
        self._refresh_views()

    def _on_link_tasks(self):
        """Link selected tasks in sequence (FS)."""
        indices = self.task_table.get_selected_task_indices()
        if len(indices) < 2:
            return
        self._save_state()

        dep_id = max((d.get("id", 0) for d in self._dependencies), default=0) + 1
        for i in range(len(indices) - 1):
            pred_id = self._tasks[indices[i]]["id"]
            succ_id = self._tasks[indices[i + 1]]["id"]
            # Check if dependency already exists
            exists = any(
                d["predecessor_id"] == pred_id and d["successor_id"] == succ_id
                for d in self._dependencies
            )
            if not exists:
                self._dependencies.append({
                    "id": dep_id,
                    "predecessor_id": pred_id,
                    "successor_id": succ_id,
                    "dep_type": "FS",
                    "lag": 0,
                })
                dep_id += 1

        self._refresh_views()

    def _on_unlink_tasks(self):
        """Remove dependencies between selected tasks."""
        indices = self.task_table.get_selected_task_indices()
        if len(indices) < 2:
            return
        self._save_state()

        task_ids = {self._tasks[i]["id"] for i in indices}
        self._dependencies = [
            d for d in self._dependencies
            if not (d["predecessor_id"] in task_ids and d["successor_id"] in task_ids)
        ]
        self._refresh_views()

    def _on_toggle_milestone(self):
        indices = self.task_table.get_selected_task_indices()
        if not indices:
            return
        self._save_state()

        for idx in indices:
            task = self._tasks[idx]
            task["is_milestone"] = not task.get("is_milestone", False)
            if task["is_milestone"]:
                task["duration"] = 0
                task["end_date"] = task.get("start_date")
            else:
                task["duration"] = 1

        self._refresh_views()

        self._refresh_views()

    def _on_task_moved(self, source_row: int, target_row: int):
        """Handle drag-and-drop row reordering in the task table."""
        if source_row == target_row:
            return
        self._save_state()
        task = self._tasks.pop(source_row)
        
        # If moving down, target index shifts after pop
        if source_row < target_row:
            target_row -= 1
            
        self._tasks.insert(target_row, task)
        self._recalculate_wbs()
        self._refresh_views()

    def _on_dependency_drawn(self, src_id: int, tgt_id: int):
        """Handle drag-and-drop dependency creation in the network chart."""
        if src_id == tgt_id:
            return

        # Check if dependency already exists
        exists = any(
            d["predecessor_id"] == src_id and d["successor_id"] == tgt_id
            for d in self._dependencies
        )
        if exists:
            return
            
        # Prevent dependency cycles
        def has_cycle(current, start, visited=None):
            if visited is None:
                visited = set()
            if current == start:
                return True
            if current in visited:
                return False
            visited.add(current)
            for d in self._dependencies:
                if d["predecessor_id"] == current:
                    if has_cycle(d["successor_id"], start, visited):
                        return True
            return False

        if has_cycle(tgt_id, src_id):
            self.status_bar.showMessage("❌ 循環する依存関係は作成できません。", 3000)
            return

        self._save_state()
        dep_id = max((d.get("id", 0) for d in self._dependencies), default=0) + 1
        self._dependencies.append({
            "id": dep_id,
            "predecessor_id": src_id,
            "successor_id": tgt_id,
            "dep_type": "FS",
            "lag": 0
        })
        self._refresh_views()
        self.status_bar.showMessage("🔗 依存関係(FS)を追加しました。", 3000)

    def _on_gantt_task_date_changed(self, task_id: int, new_start: date, new_end: date):
        """Handle task resize from Gantt chart."""
        self._save_state()
        for t in self._tasks:
            if t["id"] == task_id:
                t["start_date"] = new_start
                t["end_date"] = new_end
                t["duration"] = max(1, (new_end - new_start).days + 1)
                break
        self._recalculate_wbs()
        self._refresh_views()
        self.status_bar.showMessage("📅 タスクの期間を変更しました。", 3000)

    def _on_task_info(self):
        task = self.task_table.get_selected_task()
        if not task:
            return
        self._save_state()

        dlg = TaskDialog(task, self)
        if dlg.exec() == TaskDialog.DialogCode.Accepted:
            result = dlg.get_result()
            # Find and update in list
            for i, t in enumerate(self._tasks):
                if t["id"] == result["id"]:
                    self._tasks[i].update(result)
                    break
            self._recalculate_wbs()
            self._refresh_views()

    def _on_cut_task(self):
        """Cut selected tasks to clipboard."""
        indices = self.task_table.get_selected_task_indices()
        if not indices:
            return
        self._save_state()

        # Copy selected tasks to clipboard
        self._clipboard = [copy.deepcopy(self._tasks[i]) for i in indices]

        # Remove selected tasks (reverse order to preserve indices)
        removed_ids = set()
        for idx in reversed(indices):
            if 0 <= idx < len(self._tasks):
                removed_ids.add(self._tasks[idx]["id"])
                self._tasks.pop(idx)

        # Remove dependencies involving removed tasks
        self._dependencies = [
            d for d in self._dependencies
            if d["predecessor_id"] not in removed_ids and d["successor_id"] not in removed_ids
        ]

        self._recalculate_wbs()
        self._refresh_views()
        self.status_bar.showMessage(f"{len(self._clipboard)}件のタスクをカットしました", 3000)

    def _on_paste_task(self):
        """Paste tasks from clipboard."""
        if not self._clipboard:
            return
        self._save_state()

        selected = self.task_table.get_selected_task_indices()
        insert_at = selected[-1] + 1 if selected else len(self._tasks)

        for i, task_data in enumerate(self._clipboard):
            new_task = copy.deepcopy(task_data)
            new_task["id"] = self._next_task_id
            self._next_task_id += 1
            self._tasks.insert(insert_at + i, new_task)

        self._recalculate_wbs()
        self._refresh_views()
        self.status_bar.showMessage(f"{len(self._clipboard)}件のタスクをペーストしました", 3000)

    def _on_task_data_changed(self):
        """Handle inline edit in task table."""
        self._tasks = self.task_table.get_model().get_flat_tasks()
        self._parse_predecessors_from_tasks()
        self._recalculate_wbs()
        # Refresh gantt only (table already has changes)
        self.gantt.load_tasks(self._tasks, self._dependencies)
        self._update_status_bar()

    def _on_scroll_today(self):
        self.gantt.chart.scroll_to_today()

    def _on_set_baseline(self):
        self._save_state()
        for task in self._tasks:
            task["baseline_start"] = task.get("start_date")
            task["baseline_end"] = task.get("end_date")
            task["baseline_duration"] = task.get("duration")
        self.status_bar.showMessage("ベースラインを設定しました", 3000)

    # ========== Undo / Redo ==========

    def _on_undo(self):
        if not self._undo_stack:
            return
        current = {
            "tasks": copy.deepcopy(self._tasks),
            "dependencies": copy.deepcopy(self._dependencies),
        }
        self._redo_stack.append(current)

        state = self._undo_stack.pop()
        self._tasks = state["tasks"]
        self._dependencies = state["dependencies"]
        self._refresh_views()

    def _on_redo(self):
        if not self._redo_stack:
            return
        current = {
            "tasks": copy.deepcopy(self._tasks),
            "dependencies": copy.deepcopy(self._dependencies),
        }
        self._undo_stack.append(current)

        state = self._redo_stack.pop()
        self._tasks = state["tasks"]
        self._dependencies = state["dependencies"]
        self._refresh_views()

    # ========== File Operations ==========

    def _on_new_project(self):
        reply = QMessageBox.question(
            self, "新規プロジェクト",
            "現在のプロジェクトを閉じて新規プロジェクトを作成しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._tasks = []
            self._dependencies = []
            self._resources = []
            self._project = {"name": "新規プロジェクト", "start_date": date.today()}
            self._next_task_id = 1
            self._undo_stack.clear()
            self._redo_stack.clear()
            self._refresh_views()

    def _on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "プロジェクトを保存", "",
            "Bokmål Project (*.bokmal);;JSON (*.json);;All Files (*)"
        )
        if path:
            data = {
                "project": self._project,
                "tasks": self._tasks,
                "dependencies": self._dependencies,
                "resources": self._resources,
            }
            json_str = project_to_json(data)
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.status_bar.showMessage(f"保存しました: {path}", 3000)

    def _auto_backup(self):
        """Automatically backup the current project state."""
        if not self._tasks:
            return  # Nothing to backup
        
        data = {
            "project": self._project,
            "tasks": self._tasks,
            "dependencies": self._dependencies,
            "resources": self._resources,
        }
        json_str = project_to_json(data)
        
        import os
        from pathlib import Path
        if self._current_file:
            # Backup next to the current file
            backup_path = Path(self._current_file).with_name(f".{Path(self._current_file).name}.backup")
        else:
            # Generic backup in data folder
            from config import DB_PATH
            backup_path = DB_PATH / "bokmal_auto_backup.json"
            
        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.status_bar.showMessage(f"自動バックアップを作成しました: {backup_path.name}", 3000)
        except Exception as e:
            print(f"Auto-backup failed: {e}")

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "プロジェクトを開く", "",
            "Bokmål Project (*.bokmal);;JSON (*.json);;All Files (*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json_to_project(f.read())
            self._project = data.get("project", {})
            self._tasks = data.get("tasks", [])
            self._dependencies = data.get("dependencies", [])
            self._resources = data.get("resources", [])
            self._next_task_id = max((t["id"] for t in self._tasks), default=0) + 1
            self._undo_stack.clear()
            self._redo_stack.clear()
            self._refresh_views()
            self.status_bar.showMessage(f"読み込みました: {path}", 3000)

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "CSVエクスポート", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            csv_str = tasks_to_csv(self._tasks)
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write(csv_str)
            self.status_bar.showMessage(f"CSVエクスポート完了: {path}", 3000)

    def _on_import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "CSVインポート", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self._save_state()
            with open(path, "r", encoding="utf-8-sig") as f:
                imported = csv_to_tasks(f.read())
            self._tasks = imported
            self._next_task_id = max((t["id"] for t in self._tasks), default=0) + 1
            self._recalculate_wbs()
            self._refresh_views()
            self.status_bar.showMessage(f"CSVインポート完了: {path}", 3000)



    # ========== Helpers ==========

    def _sync_predecessors_to_tasks(self):
        """Generate predecessors display string using task IDs."""
        # Build lookup: successor_id -> list of (pred_id, type, lag)
        succ_map: dict[int, list[tuple[int, str, int]]] = {}
        for dep in self._dependencies:
            sid = dep["successor_id"]
            succ_map.setdefault(sid, []).append(
                (dep["predecessor_id"], dep.get("dep_type", "FS"), dep.get("lag", 0))
            )

        for task in self._tasks:
            preds = succ_map.get(task["id"], [])
            if preds:
                parts = []
                for pred_id, dep_type, lag in preds:
                    s = str(pred_id) + dep_type
                    if lag > 0:
                        s += f"+{lag}d"
                    elif lag < 0:
                        s += f"{lag}d"
                    parts.append(s)
                task["predecessors"] = ", ".join(parts)
            else:
                task["predecessors"] = ""

    def _parse_predecessors_from_tasks(self):
        """Parse predecessors strings (task IDs) back into dependency data."""
        valid_ids = {t["id"] for t in self._tasks}

        new_deps: list[dict] = []
        dep_id = 1
        pattern = re.compile(r"(\d+)\s*(FS|FF|SS|SF)?\s*([+-]\d+)?d?", re.IGNORECASE)

        for task in self._tasks:
            pred_str = task.get("predecessors", "").strip()
            if not pred_str:
                continue
            for part in pred_str.split(","):
                part = part.strip()
                if not part:
                    continue
                m = pattern.match(part)
                if m:
                    pred_task_id = int(m.group(1))
                    if pred_task_id not in valid_ids:
                        continue  # invalid task ID
                    dep_type = (m.group(2) or "FS").upper()
                    lag = int(m.group(3)) if m.group(3) else 0
                    new_deps.append({
                        "id": dep_id,
                        "predecessor_id": pred_task_id,
                        "successor_id": task["id"],
                        "dep_type": dep_type,
                        "lag": lag,
                    })
                    dep_id += 1

        self._dependencies = new_deps

    def _recalculate_wbs(self):
        """Recalculate WBS for all tasks."""
        task_objs = _wrap_tasks(self._tasks)
        WBSManager.recalculate_all(task_objs)
        _unwrap_tasks(task_objs, self._tasks)

        # Update sort order
        for i, task in enumerate(self._tasks):
            task["sort_order"] = i

    def _on_export_excel(self):
        """Export tasks to Excel format (.xlsx)"""
        path, _ = QFileDialog.getSaveFileName(self, "Excelエクスポート", "", "Excel Files (*.xlsx)")
        if path:
            success = export_tasks_to_excel(self._tasks, path)
            if success:
                self.status_bar.showMessage(f"Excelへエクスポートしました: {path}", 5000)
            else:
                QMessageBox.warning(self, "エラー", "openpyxl ライブラリがインストールされていません。\nターミナルで 'pip install openpyxl' を実行してください。")

    def _on_export_pptx(self):
        """Export Gantt chart to PowerPoint format (.pptx)"""
        path, _ = QFileDialog.getSaveFileName(self, "PowerPointエクスポート", "", "PowerPoint Files (*.pptx)")
        if path:
            try:
                export_gantt_to_pptx(
                    self._tasks, self._dependencies, path,
                    self._project.get("name", "")
                )
                self.status_bar.showMessage(f"PowerPointへエクスポートしました: {path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"PPTXの書き出しに失敗しました:\n{e}")

    def _on_toggle_wbs(self):
        """Toggle WBS panel visibility by adjusting splitter sizes."""
        sizes = self.splitter.sizes()
        if len(sizes) == 2:
            if sizes[0] == 0:
                total = sum(sizes)
                if total == 0:
                    total = 1000
                self.splitter.setSizes([int(total * 0.4), int(total * 0.6)])
            else:
                total = sum(sizes)
                self.splitter.setSizes([0, total])

    def _on_sort_waterfall(self):
        """Sort tasks in waterfall order (hierarchical, ascending start date)."""
        self._save_state()

        nodes = {}
        for t in self._tasks:
            nodes[t["id"]] = {"task": t, "children": []}

        wbs_to_id = {t["wbs"]: t["id"] for t in self._tasks if t.get("wbs")}

        root_nodes = []
        for t in self._tasks:
            wbs = t.get("wbs", "")
            if "." in wbs:
                parent_wbs = wbs.rsplit(".", 1)[0]
                if parent_wbs in wbs_to_id:
                    parent_id = wbs_to_id[parent_wbs]
                    nodes[parent_id]["children"].append(nodes[t["id"]])
                else:
                    root_nodes.append(nodes[t["id"]])
            else:
                root_nodes.append(nodes[t["id"]])

        def get_sort_key(node):
            task = node["task"]
            sd = task.get("start_date")
            ed = task.get("end_date")
            from datetime import date
            max_dt = date(2100, 1, 1)
            return (sd if sd else max_dt, ed if ed else max_dt, task["id"])

        def sort_tree(node_list):
            node_list.sort(key=get_sort_key)
            for n in node_list:
                sort_tree(n["children"])

        sort_tree(root_nodes)

        new_tasks = []
        def traverse(node_list):
            for n in node_list:
                new_tasks.append(n["task"])
                traverse(n["children"])
        
        traverse(root_nodes)
        self._tasks = new_tasks
        
        self._recalculate_wbs()
        self._refresh_views()
        self.status_bar.showMessage("🌊 タスクをウォーターフォール順に並べ替えました。", 4000)

    def _on_resource_added(self, res_data: dict):
        """Handle new resource added from ResourceSheetView."""
        next_id = 1
        if self._resources:
            next_id = max(r.get("id", 0) for r in self._resources) + 1
        res_data["id"] = next_id
        self._resources.append(res_data)
        self._refresh_views()
        self._push_undo("Add Resource")

    def _on_resource_updated(self):
        """Handle resource edits."""
        self._refresh_views()
        self._push_undo("Edit Resource")

    def _on_about(self):
        QMessageBox.about(
            self, "Bokmålについて",
            "<h2>Bokmål Project Manager</h2>"
            "<p>Version 0.1.0</p>"
            "<p>Python 3.13 + PySide6で構築されたプロジェクト管理アプリケーション。</p>"
            "<p>Microsoft Projectのような機能をPythonで実現します。</p>"
        )


# ========== Helper: dict <-> object bridge for WBSManager ==========

class _TaskWrapper:
    """Minimal wrapper to make dicts behave like objects for WBSManager."""
    def __init__(self, d: dict):
        self._d = d

    def __getattr__(self, name):
        if name == "_d":
            return super().__getattribute__("_d")
        return self._d.get(name)

    def __setattr__(self, name, value):
        if name == "_d":
            super().__setattr__(name, value)
        else:
            self._d[name] = value


def _wrap_tasks(tasks: list[dict]) -> list[_TaskWrapper]:
    return [_TaskWrapper(t) for t in tasks]


def _unwrap_tasks(wrappers: list[_TaskWrapper], original: list[dict]):
    for w, t in zip(wrappers, original):
        t.update(w._d)
