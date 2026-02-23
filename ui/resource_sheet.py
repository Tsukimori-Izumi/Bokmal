"""Resource Sheet View."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView,
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QColor, QFont

from ui.theme import COLORS
from models.resource import ResourceType

RESOURCE_COLUMNS = [
    {"key": "name", "label": "リソース名", "width": 200},
    {"key": "resource_type", "label": "種類", "width": 80},
    {"key": "max_units", "label": "最大単位", "width": 80},
    {"key": "standard_rate", "label": "標準単価", "width": 100},
    {"key": "overtime_rate", "label": "超過単価", "width": 100},
    {"key": "email", "label": "メール", "width": 150},
]


class ResourceTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._resources: list[dict] = []

    def load(self, resources: list[dict]):
        self.beginResetModel()
        self._resources = resources
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._resources)

    def columnCount(self, parent=QModelIndex()):
        return len(RESOURCE_COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        res = self._resources[index.row()]
        col = RESOURCE_COLUMNS[index.column()]
        key = col["key"]
        value = res.get(key, "")

        if role == Qt.ItemDataRole.DisplayRole:
            if key == "resource_type":
                return ResourceType.LABELS.get(value, value)
            if key in ("standard_rate", "overtime_rate"):
                return f"¥{value:,.0f}/時" if value else ""
            if key == "max_units":
                return f"{value:.0f}%" if value else "100%"
            return str(value) if value else ""
        elif role == Qt.ItemDataRole.ForegroundRole:
            return QColor(COLORS["text_primary"])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return RESOURCE_COLUMNS[section]["label"]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            res = self._resources[index.row()]
            key = RESOURCE_COLUMNS[index.column()]["key"]
            
            # Simple type parsing
            val_str = str(value).strip().replace("¥", "").replace(",", "").replace("%", "").replace("/時", "")
            
            if key in ("max_units", "standard_rate", "overtime_rate"):
                try:
                    res[key] = float(val_str)
                except ValueError:
                    pass
            else:
                res[key] = val_str
                
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            return True
        return False


class ResourceSheetView(QWidget):
    resource_added = Signal(dict)
    resource_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ リソース追加")
        btn_add.setFixedHeight(30)
        btn_add.clicked.connect(self._on_add)
        btn_layout.addWidget(btn_add)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(30)

        self._model = ResourceTableModel(self)
        self.table.setModel(self._model)

        header = self.table.horizontalHeader()
        for i, col in enumerate(RESOURCE_COLUMNS):
            header.resizeSection(i, col["width"])
        header.setStretchLastSection(True)

        layout.addWidget(self.table)

    def load_resources(self, resources: list[dict]):
        self._model.load(resources)
        
        # Connect model dataChanged to emit our own update signal
        try:
            self._model.dataChanged.disconnect(self._on_model_data_changed)
        except:
            pass
        self._model.dataChanged.connect(self._on_model_data_changed)

    def _on_model_data_changed(self, top_left, bottom_right, roles):
        self.resource_updated.emit()

    def _on_add(self):
        new_res = {
            "name": "新しいリソース",
            "resource_type": ResourceType.WORK,
            "max_units": 100.0,
            "standard_rate": 0.0,
            "overtime_rate": 0.0,
            "cost_per_use": 0.0,
            "email": "",
            "notes": ""
        }
        self.resource_added.emit(new_res)
