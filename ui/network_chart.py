"""Network Chart - PERT/dependency network diagram for task relationships."""

from datetime import date

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QPainterPath
)

from ui.theme import COLORS


NODE_WIDTH = 220
NODE_HEIGHT = 80
H_SPACING = 60
V_SPACING = 40


class TaskNode(QGraphicsRectItem):
    """Visual node for a task in the network diagram."""

    def __init__(self, task: dict, x: float, y: float):
        super().__init__(0, 0, NODE_WIDTH, NODE_HEIGHT)
        self.task = task
        self.node_x = x
        self.node_y = y

        # Position the item in the scene
        self.setPos(x, y)

        # Determine color
        if task.get("is_milestone"):
            self._color = QColor(COLORS["milestone"])
        elif task.get("is_summary"):
            self._color = QColor(COLORS["summary_bar"])
        elif task.get("is_critical"):
            self._color = QColor(COLORS["critical"])
        else:
            self._color = QColor(COLORS["accent"])

        self.setBrush(QBrush(self._color))
        self.setPen(QPen(self._color.lighter(130), 2))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

        # Pre-compute text lines
        self._name = task.get("name", "")
        duration = task.get("duration", 0)
        progress = task.get("progress", 0)
        if task.get("is_milestone"):
            self._info = f"◆ マイルストーン | {progress:.0f}%"
        else:
            self._info = f"{duration}日 | {progress:.0f}%"

        start = task.get("start_date")
        end = task.get("end_date")
        if isinstance(start, date) and isinstance(end, date):
            self._dates = f"{start.strftime('%m/%d')} ~ {end.strftime('%m/%d')}"
        else:
            self._dates = ""

    def center_right(self) -> QPointF:
        return QPointF(self.node_x + NODE_WIDTH, self.node_y + NODE_HEIGHT / 2)

    def center_left(self) -> QPointF:
        return QPointF(self.node_x, self.node_y + NODE_HEIGHT / 2)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # Draw rounded rectangle background
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, self.brush())
        painter.setPen(self.pen())
        painter.drawPath(path)

        # Draw task name (bold, white)
        name_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(name_font)
        painter.setPen(QColor("#ffffff"))
        name_rect = QRectF(8, 6, NODE_WIDTH - 16, 22)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._name)

        # Draw info line (small, light)
        info_font = QFont("Segoe UI", 8)
        painter.setFont(info_font)
        painter.setPen(QColor("#ccccdd"))
        info_rect = QRectF(8, 30, NODE_WIDTH - 16, 18)
        painter.drawText(info_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._info)

        # Draw date range (small, dimmer)
        painter.setPen(QColor("#aaaacc"))
        date_rect = QRectF(8, 50, NODE_WIDTH - 16, 18)
        painter.drawText(date_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._dates)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            views = self.scene().views()
            if views:
                views[0].start_drag_line(self)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        views = self.scene().views()
        if views:
            views[0].update_drag_line(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        views = self.scene().views()
        if views:
            if event.button() == Qt.MouseButton.LeftButton:
                views[0].finish_drag_line(self, event.scenePos())
        try:
            super().mouseReleaseEvent(event)
        except RuntimeError:
            pass


class NetworkChartView(QGraphicsView):
    """Network diagram showing tasks and their dependency relationships."""

    dependency_drawn = Signal(int, int)  # source_id, target_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._nodes: dict[int, TaskNode] = {}
        # Dark background
        self._scene.setBackgroundBrush(QBrush(QColor(COLORS["gantt_bg"])))

        self._drag_line = None
        self._drag_source_node = None

    def start_drag_line(self, source_node: TaskNode):
        self._drag_source_node = source_node
        start_pt = source_node.center_right()
        self._drag_line = QGraphicsLineItem(start_pt.x(), start_pt.y(), start_pt.x(), start_pt.y())
        pen = QPen(QColor(COLORS.get("progress", "#4EC9B0")), 2, Qt.PenStyle.DashLine)
        self._drag_line.setPen(pen)
        self._scene.addItem(self._drag_line)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)  # Handle dragging items manually

    def update_drag_line(self, pos: QPointF):
        if self._drag_line and self._drag_source_node:
            start_pt = self._drag_source_node.center_right()
            self._drag_line.setLine(start_pt.x(), start_pt.y(), pos.x(), pos.y())

    def finish_drag_line(self, source_node: TaskNode, pos: QPointF):
        if self._drag_line:
            self._scene.removeItem(self._drag_line)
            self._drag_line = None
            
            # Find item under pos
            items = self._scene.items(pos)
            target_node = None
            for item in items:
                if isinstance(item, TaskNode) and item != source_node:
                    target_node = item
                    break
            
            if target_node:
                self.dependency_drawn.emit(source_node.task["id"], target_node.task["id"])
            
            self._drag_source_node = None
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def load_tasks(self, tasks: list[dict], dependencies: list[dict]):
        """Layout tasks as a network diagram."""
        self._scene.clear()
        self._nodes.clear()

        if not tasks:
            return

        # Build adjacency lists
        successors: dict[int, list[int]] = {}
        predecessors_map: dict[int, list[int]] = {}
        task_ids = {t["id"] for t in tasks}

        for dep in dependencies:
            pid = dep.get("predecessor_id")
            sid = dep.get("successor_id")
            if pid in task_ids and sid in task_ids:
                successors.setdefault(pid, []).append(sid)
                predecessors_map.setdefault(sid, []).append(pid)

        # Assign layers (topological sort / longest path)
        task_map = {t["id"]: t for t in tasks}
        layers: dict[int, int] = {}
        self._compute_layers(tasks, predecessors_map, layers)

        # Group by layer
        layer_groups: dict[int, list[int]] = {}
        for tid, layer in layers.items():
            layer_groups.setdefault(layer, []).append(tid)

        max_layer = max(layers.values()) if layers else 0

        # Position nodes
        for layer_idx in range(max_layer + 1):
            group = layer_groups.get(layer_idx, [])
            x = 50 + layer_idx * (NODE_WIDTH + H_SPACING)
            for row, tid in enumerate(group):
                y = 50 + row * (NODE_HEIGHT + V_SPACING)
                task = task_map.get(tid)
                if task:
                    node = TaskNode(task, x, y)
                    self._scene.addItem(node)
                    self._nodes[tid] = node

        # Draw edges
        arrow_pen = QPen(QColor(COLORS["accent_light"]), 2)
        critical_pen = QPen(QColor(COLORS["critical"]), 2.5)

        for dep in dependencies:
            pid = dep.get("predecessor_id")
            sid = dep.get("successor_id")
            if pid in self._nodes and sid in self._nodes:
                p_node = self._nodes[pid]
                s_node = self._nodes[sid]

                start = p_node.center_right()
                end = s_node.center_left()

                # Determine if on critical path
                is_critical = (task_map.get(pid, {}).get("is_critical") and
                               task_map.get(sid, {}).get("is_critical"))
                pen = critical_pen if is_critical else arrow_pen

                # Draw line with routing
                mid_x = (start.x() + end.x()) / 2
                path = QPainterPath()
                path.moveTo(start)
                path.cubicTo(
                    QPointF(mid_x, start.y()),
                    QPointF(mid_x, end.y()),
                    end
                )
                path_item = self._scene.addPath(path, pen)

                # Arrowhead
                arrow_size = 8
                angle_line = end - QPointF(mid_x, end.y())
                if angle_line.x() == 0 and angle_line.y() == 0:
                    angle_line = QPointF(1, 0)
                length = (angle_line.x() ** 2 + angle_line.y() ** 2) ** 0.5
                unit = QPointF(angle_line.x() / length, angle_line.y() / length)
                perp = QPointF(-unit.y(), unit.x())

                p1 = end - unit * arrow_size + perp * arrow_size * 0.5
                p2 = end - unit * arrow_size - perp * arrow_size * 0.5

                arrow = QPolygonF([end, p1, p2])
                arrow_item = self._scene.addPolygon(
                    arrow, pen, QBrush(pen.color())
                )

        # Fit scene
        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-30, -30, 30, 30))

    def _compute_layers(self, tasks, predecessors_map, layers):
        """Compute layer for each task using longest path."""
        task_map = {t["id"]: t for t in tasks}
        visited = set()

        def get_layer(tid):
            if tid in layers:
                return layers[tid]
            if tid in visited:
                return 0  # cycle protection
            visited.add(tid)
            preds = predecessors_map.get(tid, [])
            if not preds:
                layers[tid] = 0
            else:
                layers[tid] = max(get_layer(p) + 1 for p in preds)
            return layers[tid]

        for t in tasks:
            get_layer(t["id"])


class NetworkWidget(QWidget):
    """Complete network chart widget with header."""

    dependency_drawn = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QFrame(self)
        header.setFixedHeight(32)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_header']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 12, 0)

        title = QLabel("📊 ネットワークチャート")
        title.setStyleSheet(f"color: {COLORS['accent_light']}; font-weight: bold;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        legend_crit = QLabel("■ クリティカル")
        legend_crit.setStyleSheet(f"color: {COLORS['critical']}; font-size: 11px;")
        h_layout.addWidget(legend_crit)

        legend_normal = QLabel("■ 通常")
        legend_normal.setStyleSheet(f"color: {COLORS['accent']}; font-size: 11px;")
        h_layout.addWidget(legend_normal)

        legend_ms = QLabel("■ マイルストーン")
        legend_ms.setStyleSheet(f"color: {COLORS['milestone']}; font-size: 11px;")
        h_layout.addWidget(legend_ms)

        layout.addWidget(header)

        self.chart = NetworkChartView(self)
        self.chart.dependency_drawn.connect(self.dependency_drawn.emit)
        layout.addWidget(self.chart)

    def load_tasks(self, tasks, dependencies):
        self.chart.load_tasks(tasks, dependencies)
