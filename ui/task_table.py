"""Task Table - QTreeView-based spreadsheet for tasks with WBS hierarchy."""

from datetime import date
from PySide6.QtWidgets import (
    QTreeView, QHeaderView, QStyledItemDelegate, QLineEdit,
    QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox, QWidget, QHBoxLayout,
    QProgressBar, QStyleOptionViewItem, QAbstractItemView, QStyle, QSlider
)
from PySide6.QtCore import (
    Qt, QAbstractItemModel, QModelIndex, Signal, QDate, QRect, QSize, QMimeData, QByteArray
)
from PySide6.QtGui import QPainter, QColor, QFont, QIcon, QPen, QBrush

from ui.theme import COLORS
from config import GANTT_ROW_HEIGHT, GANTT_HEADER_HEIGHT


# Column definitions
COLUMNS = [
    {"key": "name", "label": "タスク名", "width": 250, "editable": True},
    {"key": "id", "label": "#", "width": 40, "editable": False},
    {"key": "wbs", "label": "WBS", "width": 60, "editable": False},
    {"key": "duration", "label": "期間", "width": 60, "editable": True},
    {"key": "start_date", "label": "開始日", "width": 120, "editable": True},
    {"key": "end_date", "label": "終了日", "width": 120, "editable": True},
    {"key": "actual_start", "label": "実績開始日", "width": 120, "editable": True},
    {"key": "actual_end", "label": "実績終了日", "width": 120, "editable": True},
    {"key": "progress", "label": "進捗率", "width": 70, "editable": True},
    {"key": "predecessors", "label": "先行タスク", "width": 80, "editable": True},
    {"key": "resource_names", "label": "リソース", "width": 100, "editable": True},
]


class TaskTreeItem:
    """Wrapper for hierarchical task display in tree model."""

    def __init__(self, task_data: dict, parent=None):
        self.task_data = task_data
        self.parent_item = parent
        self.child_items: list[TaskTreeItem] = []

    def append_child(self, child):
        self.child_items.append(child)

    def child(self, row: int):
        if 0 <= row < len(self.child_items):
            return self.child_items[row]
        return None

    def child_count(self) -> int:
        return len(self.child_items)

    def row(self) -> int:
        if self.parent_item and self in self.parent_item.child_items:
            return self.parent_item.child_items.index(self)
        return 0

    def data(self, column: int):
        if column < 0 or column >= len(COLUMNS):
            return None
        key = COLUMNS[column]["key"]
        return self.task_data.get(key, "")


class TaskTreeModel(QAbstractItemModel):
    """Custom tree model for task hierarchy display."""

    data_changed_signal = Signal()
    task_moved = Signal(int, int)  # source_row, target_row

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = TaskTreeItem({"name": "root"})
        self._flat_tasks: list[dict] = []

    def load_tasks(self, tasks: list[dict]):
        """Load flat task list and build tree structure."""
        self.beginResetModel()
        self.root_item = TaskTreeItem({"name": "root"})
        self._flat_tasks = tasks

        # Build tree from flat list using wbs_level
        item_stack: list[TaskTreeItem] = [self.root_item]

        for task_data in tasks:
            level = task_data.get("wbs_level", 0)
            item = TaskTreeItem(task_data)

            # Find correct parent
            while len(item_stack) > level + 1:
                item_stack.pop()

            parent = item_stack[-1]
            item.parent_item = parent
            parent.append_child(item)

            item_stack.append(item)

        self.endResetModel()

    def get_flat_tasks(self) -> list[dict]:
        return self._flat_tasks

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return self.root_item.child_count()
        parent_item = parent.internalPointer()
        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item: TaskTreeItem = index.internalPointer()
        col = index.column()
        key = COLUMNS[col]["key"]
        value = item.task_data.get(key, "")

        if role == Qt.ItemDataRole.DisplayRole:
            if key == "id":
                return str(item.task_data.get("id", ""))
            elif key in ("start_date", "end_date", "actual_start", "actual_end"):
                if isinstance(value, date):
                    return value.strftime("%Y/%m/%d")
                return str(value) if value else ""
            elif key == "progress":
                return f"{value:.0f}%" if value is not None else "0%"
            elif key == "duration":
                if item.task_data.get("is_milestone"):
                    return "0日"
                return f"{value}日" if value else "1日"
            elif key == "cost":
                return f"¥{value:,.0f}" if value else ""
            return str(value) if value is not None else ""

        elif role == Qt.ItemDataRole.EditRole:
            return value

        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            if item.task_data.get("is_summary"):
                font.setBold(True)
            if item.task_data.get("is_milestone"):
                font.setItalic(True)
            return font

        elif role == Qt.ItemDataRole.ForegroundRole:
            if item.task_data.get("is_critical"):
                return QColor(COLORS["critical"])
            if item.task_data.get("is_summary"):
                return QColor(COLORS["accent_light"])
            return QColor(COLORS["text_primary"])

        elif role == Qt.ItemDataRole.BackgroundRole:
            if item.task_data.get("is_milestone"):
                return QColor(COLORS["milestone"]).darker(400)
            return None

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if key in ("duration", "progress", "cost"):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        # Custom roles
        elif role == Qt.ItemDataRole.UserRole:
            return item.task_data

        elif role == Qt.ItemDataRole.UserRole + 1:
            return item.task_data.get("id")

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        item: TaskTreeItem = index.internalPointer()
        col = index.column()
        key = COLUMNS[col]["key"]

        item.task_data[key] = value
        self.dataChanged.emit(index, index, [role])
        self.data_changed_signal.emit()
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        flags = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |
                 Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)
        col = index.column()
        if COLUMNS[col]["editable"]:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return ["application/x-bokmal-task-row"]

    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        # Find unique rows being dragged
        rows = list({idx.row() for idx in indexes if idx.column() == 0})
        if rows:
            # We only support single row move
            item = indexes[0].internalPointer()
            try:
                flat_idx = self._flat_tasks.index(item.task_data)
                encoded_data = QByteArray(str(flat_idx).encode("utf-8"))
                mime_data.setData("application/x-bokmal-task-row", encoded_data)
            except ValueError:
                pass
        return mime_data

    def dropMimeData(self, data: QMimeData, action, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.DropAction.IgnoreAction:
            return True
        if not data.hasFormat("application/x-bokmal-task-row"):
            return False

        source_flat_row = int(data.data("application/x-bokmal-task-row").data().decode("utf-8"))

        # Determine target flat row
        target_flat_row = len(self._flat_tasks)  # default to end
        if row != -1:
            # Dropped between rows
            if parent.isValid():
                parent_item = parent.internalPointer()
                if row < parent_item.child_count():
                    target_item = parent_item.child_items[row]
                    try:
                        target_flat_row = self._flat_tasks.index(target_item.task_data)
                    except ValueError:
                        pass
                else:
                    try:
                        target_flat_row = self._flat_tasks.index(parent_item.task_data) + 1
                    except ValueError:
                        pass
            else:
                # Dropped at root level
                if row < self.root_item.child_count():
                    target_item = self.root_item.child_items[row]
                    try:
                        target_flat_row = self._flat_tasks.index(target_item.task_data)
                    except ValueError:
                        pass
        elif parent.isValid():
            # Dropped ON top of an item
            parent_item = parent.internalPointer()
            try:
                target_flat_row = self._flat_tasks.index(parent_item.task_data)
            except ValueError:
                pass

        if source_flat_row == target_flat_row or source_flat_row + 1 == target_flat_row:
            return False

        self.task_moved.emit(source_flat_row, target_flat_row)
        return True

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(COLUMNS):
                return COLUMNS[section]["label"]
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_item: TaskTreeItem = index.internalPointer()
        parent_item = child_item.parent_item
        if parent_item is None or parent_item == self.root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def get_task_by_index(self, index: QModelIndex) -> dict | None:
        if index.isValid():
            item: TaskTreeItem = index.internalPointer()
            return item.task_data
        return None


class TaskItemDelegate(QStyledItemDelegate):
    """Custom delegate for task table cells."""

    def createEditor(self, parent, option, index):
        col = index.column()
        key = COLUMNS[col]["key"]

        if key == "name":
            editor = QLineEdit(parent)
            return editor
        elif key == "duration":
            editor = QSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(9999)
            editor.setSuffix("日")
            return editor
        elif key in ("start_date", "end_date", "actual_start", "actual_end"):
            editor = QDateEdit(parent)
            editor.setCalendarPopup(True)
            editor.setDisplayFormat("yyyy/MM/dd")
            editor.setSpecialValueText(" ")  # allow empty
            return editor
        elif key == "progress":
            editor = QSlider(Qt.Orientation.Horizontal, parent)
            editor.setRange(0, 100)
            editor.setSingleStep(5)
            editor.setPageStep(10)
            editor.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    height: 6px;
                    background: {COLORS['border']};
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                    background: {COLORS['progress']};
                }}
                QSlider::sub-page:horizontal {{
                    background: {COLORS['progress']};
                    border-radius: 3px;
                }}
            """)
            return editor
        elif key == "cost":
            editor = QDoubleSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(999999999)
            editor.setPrefix("¥")
            editor.setDecimals(0)
            return editor
        elif key == "predecessors":
            editor = QLineEdit(parent)
            editor.setPlaceholderText("例: 1FS,2SS+1d")
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        col = index.column()
        key = COLUMNS[col]["key"]

        if isinstance(editor, QSpinBox):
            editor.setValue(int(value) if value else 0)
        elif isinstance(editor, QSlider):
            editor.setValue(int(float(value)) if value else 0)
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(value) if value else 0.0)
        elif isinstance(editor, QDateEdit):
            if isinstance(value, date):
                editor.setDate(QDate(value.year, value.month, value.day))
            else:
                editor.setDate(QDate.currentDate())
        elif isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col = index.column()
        key = COLUMNS[col]["key"]

        if isinstance(editor, QSpinBox):
            model.setData(index, editor.value())
        elif isinstance(editor, QSlider):
            model.setData(index, float(editor.value()))
        elif isinstance(editor, QDoubleSpinBox):
            model.setData(index, editor.value())
        elif isinstance(editor, QDateEdit):
            qd = editor.date()
            model.setData(index, date(qd.year(), qd.month(), qd.day()))
        elif isinstance(editor, QLineEdit):
            model.setData(index, editor.text())
        else:
            super().setModelData(editor, model, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        col = index.column()
        key = COLUMNS[col]["key"]

        if key == "progress":
            # Draw progress bar
            painter.save()
            value = index.model().data(index, Qt.ItemDataRole.EditRole)
            progress = float(value) if value else 0.0

            # Background
            painter.fillRect(option.rect, QColor(COLORS["bg_secondary"]))

            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, QColor(COLORS["selection"]))

            # Progress bar
            bar_rect = QRect(
                option.rect.x() + 4,
                option.rect.y() + option.rect.height() // 2 - 4,
                option.rect.width() - 8,
                8
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLORS["border"]))
            painter.drawRoundedRect(bar_rect, 3, 3)

            if progress > 0:
                fill_width = int(bar_rect.width() * progress / 100)
                fill_rect = QRect(bar_rect.x(), bar_rect.y(), fill_width, bar_rect.height())
                painter.setBrush(QColor(COLORS["progress"]))
                painter.drawRoundedRect(fill_rect, 3, 3)

            # Text
            painter.setPen(QColor(COLORS["text_secondary"]))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(option.rect.adjusted(4, 0, -4, 0),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{progress:.0f}%")
            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), GANTT_ROW_HEIGHT)


class TaskTableView(QTreeView):
    """Task table with WBS hierarchy, inline editing, and column management."""

    task_selected = Signal(dict)  # emitted when a task row is selected
    task_data_changed = Signal()  # emitted when task data is edited
    task_moved = Signal(int, int) # emitted when a task is drag-and-dropped
    collapse_state_changed = Signal() # emitted when a row is expanded or collapsed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        # Row height must match gantt row height
        self.setIndentation(20)

        # Enable drag-and-drop row reordering
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Set delegate
        self._delegate = TaskItemDelegate(self)
        self.setItemDelegate(self._delegate)

        # Model
        self._model = TaskTreeModel(self)
        self.setModel(self._model)
        self._model.data_changed_signal.connect(self._on_data_changed)
        self._model.task_moved.connect(self.task_moved.emit)

        # Expand/Collapse signals
        self.expanded.connect(lambda idx: self.collapse_state_changed.emit())
        self.collapsed.connect(lambda idx: self.collapse_state_changed.emit())

        # Selection
        self.selectionModel().currentChanged.connect(self._on_selection_changed)

        # Header
        header = self.header()
        for i, col in enumerate(COLUMNS):
            header.resizeSection(i, col["width"])
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        # Visually reorder: # (logical 1) | WBS (logical 2) | タスク名 (logical 0) | ...
        header.moveSection(1, 0)  # Move # to first position
        header.moveSection(2, 1)  # Move WBS to second position

        # Set table header height to match gantt header (toolbar 32px + scene header 50px)
        header.setFixedHeight(GANTT_HEADER_HEIGHT + 32)

    def load_tasks(self, tasks: list[dict]):
        """Load tasks into the tree model."""
        # Save expanded state to restore after reload
        expanded_ids = set()
        if hasattr(self, "_first_load_done"):
            def save_state(parent_index):
                for row in range(self._model.rowCount(parent_index)):
                    idx = self._model.index(row, 0, parent_index)
                    if self.isExpanded(idx):
                        task = self._model.get_task_by_index(idx)
                        if task and "id" in task:
                            expanded_ids.add(task["id"])
                        save_state(idx)
            save_state(QModelIndex())

        self._model.load_tasks(tasks)

        if not hasattr(self, "_first_load_done"):
            self.expandAll()
            self._first_load_done = True
        else:
            # Restore expanded state
            def restore_state(parent_index):
                for row in range(self._model.rowCount(parent_index)):
                    idx = self._model.index(row, 0, parent_index)
                    task = self._model.get_task_by_index(idx)
                    if task and "id" in task and task["id"] in expanded_ids:
                        self.expand(idx)
                    if self._model.rowCount(idx) > 0:
                        restore_state(idx)
            restore_state(QModelIndex())

    def get_visible_tasks(self) -> list[dict]:
        """Get tasks currently visible in the tree (not hidden by collapsed parents)."""
        visible_tasks = []
        def traverse(parent_index):
            for row in range(self._model.rowCount(parent_index)):
                idx = self._model.index(row, 0, parent_index)
                task = self._model.get_task_by_index(idx)
                if task:
                    visible_tasks.append(task)
                # Traverse children only if current node is expanded
                if self.isExpanded(idx) and self._model.rowCount(idx) > 0:
                    traverse(idx)
        traverse(QModelIndex())
        return visible_tasks

    def sizeHintForRow(self, row):
        """Force all rows to match GANTT_ROW_HEIGHT."""
        return GANTT_ROW_HEIGHT

    def get_model(self) -> TaskTreeModel:
        return self._model

    def get_selected_task(self) -> dict | None:
        index = self.currentIndex()
        return self._model.get_task_by_index(index)

    def get_selected_task_indices(self) -> list[int]:
        """Get indices of selected tasks in the flat task list."""
        indices = []
        for index in self.selectionModel().selectedRows():
            task = self._model.get_task_by_index(index)
            if task:
                flat = self._model.get_flat_tasks()
                try:
                    idx = flat.index(task)
                    indices.append(idx)
                except ValueError:
                    pass
        return sorted(indices)

    def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        task = self._model.get_task_by_index(current)
        if task:
            self.task_selected.emit(task)

    def _on_data_changed(self):
        self.task_data_changed.emit()
