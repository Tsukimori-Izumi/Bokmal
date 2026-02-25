"""Gantt Chart Widget - QGraphicsView-based interactive Gantt chart."""

from datetime import date, timedelta
import math

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QComboBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QDateTime
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QWheelEvent, QLinearGradient
)

from ui.theme import COLORS
from ui.gantt_items import TaskBarItem, DependencyArrowItem, TodayLineItem, InazumaLineItem
from config import GANTT_ROW_HEIGHT, GANTT_HEADER_HEIGHT, GANTT_DAY_WIDTH


class TimeScale:
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    AUTO = "auto"

    WIDTHS = {
        DAY: 40,
        WEEK: 20,
        MONTH: 6,
    }


class GanttScene(QGraphicsScene):
    """Custom scene for gantt chart with background grid."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_scale = TimeScale.DAY
        self.day_width = TimeScale.WIDTHS[TimeScale.DAY]
        self.row_height = GANTT_ROW_HEIGHT
        self.header_height = GANTT_HEADER_HEIGHT
        self.project_start = date.today()
        self.project_end = date.today() + timedelta(days=60)
        self.num_rows = 0

    def set_date_range(self, start: date, end: date):
        self.project_start = start - timedelta(days=3)
        self.project_end = end + timedelta(days=10)

    def set_time_scale(self, scale: str, available_width: float = 0):
        self.time_scale = scale
        if scale == TimeScale.AUTO and available_width > 0:
            total_days = max(1, (self.project_end - self.project_start).days)
            # Reserve a small margin
            self.day_width = max(0.1, (available_width - 16) / total_days)
        else:
            self.day_width = TimeScale.WIDTHS.get(scale, GANTT_DAY_WIDTH)

    def date_to_x(self, d: date) -> float:
        """Convert a date to X position."""
        delta = (d - self.project_start).days
        return delta * self.day_width

    def x_to_date(self, x: float) -> date:
        """Convert X position to date."""
        days = int(x / self.day_width)
        return self.project_start + timedelta(days=days)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draw the timeline grid background."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Background fill
        painter.fillRect(rect, QColor(COLORS["gantt_bg"]))

        total_days = (self.project_end - self.project_start).days + 1
        total_width = total_days * self.day_width
        total_height = self.header_height + self.num_rows * self.row_height

        # Clip to visible area
        left = max(0, int(rect.left()))
        right = min(int(total_width), int(rect.right()) + 1)
        top = max(0, int(rect.top()))
        bottom = min(int(total_height + 100), int(rect.bottom()) + 1)

        # --- Header background ---
        header_rect = QRectF(rect.left(), 0, rect.width(), self.header_height)
        painter.fillRect(header_rect, QColor(COLORS["gantt_header_bg"]))

        # --- Draw day columns ---
        start_day = max(0, int(left / self.day_width))
        end_day = min(total_days, int(right / self.day_width) + 1)

        grid_pen = QPen(QColor(COLORS["grid_line"]), 0.5)
        weekend_brush = QBrush(QColor(COLORS["weekend_bg"]))
        header_font = QFont("Segoe UI", 9)
        header_font_small = QFont("Segoe UI", 7)
        month_font = QFont("Segoe UI", 10, QFont.Weight.Bold)

        effective_scale = self.time_scale
        if self.time_scale == TimeScale.AUTO:
            if self.day_width < 10:
                effective_scale = TimeScale.MONTH
            elif self.day_width < 25:
                effective_scale = TimeScale.WEEK
            else:
                effective_scale = TimeScale.DAY

        for day_idx in range(start_day, end_day):
            d = self.project_start + timedelta(days=day_idx)
            x = day_idx * self.day_width

            # Weekend shading (skip if columns are too thin)
            if d.weekday() >= 5 and self.day_width > 4:
                weekend_rect = QRectF(x, self.header_height, self.day_width, total_height)
                painter.fillRect(weekend_rect, weekend_brush)

            # Vertical grid lines (based on scale)
            if effective_scale == TimeScale.DAY and self.day_width > 4:
                painter.setPen(grid_pen)
                painter.drawLine(QPointF(x, self.header_height), QPointF(x, total_height))

                # Day number in header
                painter.setPen(QColor(COLORS["text_secondary"]))
                painter.setFont(header_font_small)
                day_rect = QRectF(x, self.header_height - 20, self.day_width, 18)
                painter.drawText(day_rect, Qt.AlignmentFlag.AlignCenter, str(d.day))

            elif effective_scale == TimeScale.WEEK:
                if d.weekday() == 0:  # Monday
                    painter.setPen(grid_pen)
                    painter.drawLine(QPointF(x, self.header_height), QPointF(x, total_height))
                    painter.setPen(QColor(COLORS["text_secondary"]))
                    painter.setFont(header_font_small)
                    week_rect = QRectF(x, self.header_height - 20, 7 * self.day_width, 18)
                    painter.drawText(week_rect, Qt.AlignmentFlag.AlignCenter,
                                     f"{d.month}/{d.day}")

            elif effective_scale == TimeScale.MONTH:
                if d.day == 1:
                    painter.setPen(QPen(QColor(COLORS["border_light"]), 1))
                    painter.drawLine(QPointF(x, self.header_height), QPointF(x, total_height))

            # Month labels in upper header
            if d.day == 1 or day_idx == start_day:
                painter.setPen(QColor(COLORS["text_primary"]))
                painter.setFont(month_font)
                month_names = ["", "1月", "2月", "3月", "4月", "5月", "6月",
                               "7月", "8月", "9月", "10月", "11月", "12月"]
                month_text = f"{d.year}年 {month_names[d.month]}"
                month_rect = QRectF(x + 4, 2, 200, self.header_height / 2 - 2)
                painter.drawText(month_rect,
                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                                 month_text)

        # --- Horizontal row lines ---
        painter.setPen(grid_pen)
        for row in range(self.num_rows + 1):
            y = self.header_height + row * self.row_height
            if top <= y <= bottom:
                painter.drawLine(QPointF(left, y), QPointF(right, y))

        # --- Header bottom line ---
        painter.setPen(QPen(QColor(COLORS["border_light"]), 1))
        painter.drawLine(QPointF(left, self.header_height),
                         QPointF(right, self.header_height))


class GanttChartView(QGraphicsView):
    """Interactive Gantt chart view."""

    task_clicked = Signal(dict)
    task_date_changed = Signal(int, date, date)  # task_id, new_start, new_end

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = GanttScene(self)
        self.setScene(self._scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self._task_items: list[TaskBarItem] = []
        self._dependency_items: list[DependencyArrowItem] = []
        self._cached_tasks: list[dict] = []
        self._cached_deps: list[dict] | None = None
        self._show_today_line = True
        self._show_inazuma = False

    def set_time_scale(self, scale: str):
        available_width = self.viewport().width()
        self._scene.set_time_scale(scale, available_width)
        self._reload()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._scene.time_scale == TimeScale.AUTO:
            self.set_time_scale(TimeScale.AUTO)

    def set_display_options(self, today: bool, inazuma: bool):
        self._show_today_line = today
        self._show_inazuma = inazuma
        self._reload()

    def _reload(self):
        """Re-render with cached data using current scale."""
        if self._cached_tasks:
            self.load_tasks(self._cached_tasks, self._cached_deps)

    def load_tasks(self, tasks: list[dict], dependencies: list[dict] | None = None):
        """Render tasks and dependencies on the Gantt chart."""
        # Clear existing items
        for item in self._task_items:
            self._scene.removeItem(item)
        for item in self._dependency_items:
            self._scene.removeItem(item)
            
        if getattr(self, "_today_line", None):
            self._scene.removeItem(self._today_line)
            self._today_line = None
        if getattr(self, "_inazuma_line", None):
            self._scene.removeItem(self._inazuma_line)
            self._inazuma_line = None
            
        self._task_items.clear()
        self._dependency_items.clear()

        # Cache data for re-render on scale change
        self._cached_tasks = tasks
        self._cached_deps = dependencies

        if not tasks:
            return

        # Calculate date range
        all_starts = [t["start_date"] for t in tasks if t.get("start_date")]
        all_ends = [t["end_date"] for t in tasks if t.get("end_date")]

        if not all_starts or not all_ends:
            return

        self._scene.set_date_range(min(all_starts), max(all_ends))
        self._scene.num_rows = len(tasks)

        # Build task bar positions map
        task_positions: dict[int, tuple[float, float, float, float]] = {}  # id -> (x, y, w, h)

        for row, task in enumerate(tasks):
            start = task.get("start_date")
            end = task.get("end_date")
            if not start or not end:
                continue

            x = self._scene.date_to_x(start)
            y = self._scene.header_height + row * self._scene.row_height
            width = max(4, (end - start).days * self._scene.day_width)

            if task.get("is_milestone"):
                width = self._scene.day_width
                x -= width / 2

            bar = TaskBarItem(task, x, y, width, self._scene.row_height)
            bar.signals.date_range_changed.connect(self._on_task_bar_resized)
            self._scene.addItem(bar)
            self._task_items.append(bar)

            task_positions[task["id"]] = (x, y, width, self._scene.row_height)

        # Draw dependencies
        if dependencies:
            for dep in dependencies:
                pred_id = dep.get("predecessor_id")
                succ_id = dep.get("successor_id")
                dep_type = dep.get("dep_type", "FS")

                if pred_id in task_positions and succ_id in task_positions:
                    px, py, pw, ph = task_positions[pred_id]
                    sx, sy, sw, sh = task_positions[succ_id]

                    # Calculate start/end points based on dependency type
                    if dep_type == "FS":
                        start_pt = QPointF(px + pw, py + ph / 2)
                        end_pt = QPointF(sx, sy + sh / 2)
                    elif dep_type == "SS":
                        start_pt = QPointF(px, py + ph / 2)
                        end_pt = QPointF(sx, sy + sh / 2)
                    elif dep_type == "FF":
                        start_pt = QPointF(px + pw, py + ph / 2)
                        end_pt = QPointF(sx + sw, sy + sh / 2)
                    else:  # SF
                        start_pt = QPointF(px, py + ph / 2)
                        end_pt = QPointF(sx + sw, sy + sh / 2)

                    arrow = DependencyArrowItem(start_pt, end_pt, dep_type)
                    self._scene.addItem(arrow)
                    self._dependency_items.append(arrow)

        # Aux Lines
        today = date.today()
        today_x = self._scene.date_to_x(today)
        total_height = self._scene.header_height + len(tasks) * self._scene.row_height

        # Today Line
        if self._show_today_line:
            if self._scene.project_start <= today <= self._scene.project_end:
                self._today_line = TodayLineItem(today_x, total_height)
                self._scene.addItem(self._today_line)

        # Inazuma
        if self._show_inazuma:
            points = []
            points.append(QPointF(today_x, self._scene.header_height))
            for row, task in enumerate(tasks):
                y = self._scene.header_height + row * self._scene.row_height + self._scene.row_height / 2
                start = task.get("start_date")
                end = task.get("end_date")
                if isinstance(start, date) and isinstance(end, date):
                    prog = task.get("progress", 0) / 100.0
                    prog_days = (end - start).days * prog
                    prog_date = start + timedelta(days=prog_days)
                    px = self._scene.date_to_x(prog_date)
                    points.append(QPointF(px, y))
                else:
                    points.append(QPointF(today_x, y))
            points.append(QPointF(today_x, total_height))
            
            self._inazuma_line = InazumaLineItem(points)
            self._scene.addItem(self._inazuma_line)

        # Update scene rect
        total_days = (self._scene.project_end - self._scene.project_start).days
        self._scene.setSceneRect(
            0, 0,
            total_days * self._scene.day_width,
            self._scene.header_height + len(tasks) * self._scene.row_height + 50
        )

    def _on_task_bar_resized(self, task_id: int, new_x: float, new_width: float):
        """Handle signal from TaskBarItem being manually resized."""
        new_start = self._scene.x_to_date(new_x)
        # Calculate new end date based on new width
        # Width represents days span (excluding start day) -> width / day_width
        duration_days = round(new_width / self._scene.day_width)
        # End date is start date + duration - 1 day (if duration is inclusive)
        # However, MS Project style "end date" is usually inclusive.
        # So a 1-day task starting on Jan 1 ends on Jan 1.
        new_end = new_start + timedelta(days=max(0, duration_days - 1))
        self.task_date_changed.emit(task_id, new_start, new_end)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom on Ctrl+Scroll, otherwise scroll."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, 1)  # Only scale horizontally
        else:
            super().wheelEvent(event)

    def scroll_to_date(self, d: date):
        """Scroll view to center on a given date."""
        x = self._scene.date_to_x(d)
        self.centerOn(x, self.sceneRect().height() / 2)

    def scroll_to_today(self):
        self.scroll_to_date(date.today())


class GanttWidget(QWidget):
    """Complete Gantt widget with toolbar and chart."""

    task_clicked = Signal(dict)
    task_date_changed = Signal(int, date, date)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Mini toolbar
        toolbar = QFrame(self)
        toolbar.setFixedHeight(32)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_header']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 0, 8, 0)
        tb_layout.setSpacing(8)

        tb_layout.addWidget(QLabel("表示:"))

        self.scale_combo = QComboBox()
        self.scale_combo.addItem("日", TimeScale.DAY)
        self.scale_combo.addItem("週", TimeScale.WEEK)
        self.scale_combo.addItem("月", TimeScale.MONTH)
        self.scale_combo.addItem("全体", TimeScale.AUTO)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        self.scale_combo.setFixedWidth(70)
        tb_layout.addWidget(self.scale_combo)

        # Toggles
        self.cb_today = QCheckBox("今日線")
        self.cb_today.setChecked(True)
        self.cb_today.toggled.connect(self._on_display_toggled)
        tb_layout.addWidget(self.cb_today)

        self.cb_inazuma = QCheckBox("イナズマ線")
        self.cb_inazuma.toggled.connect(self._on_display_toggled)
        tb_layout.addWidget(self.cb_inazuma)

        tb_layout.addStretch()

        today_label = QLabel("📅 今日")
        today_label.setCursor(Qt.CursorShape.PointingHandCursor)
        today_label.mousePressEvent = lambda e: self.chart.scroll_to_today()
        today_label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        tb_layout.addWidget(today_label)

        layout.addWidget(toolbar)

        # Chart
        self.chart = GanttChartView(self)
        self.chart.task_date_changed.connect(self.task_date_changed.emit)
        layout.addWidget(self.chart)

    def load_tasks(self, tasks, dependencies=None):
        self.chart.load_tasks(tasks, dependencies)

    def _on_scale_changed(self, index):
        scale = self.scale_combo.currentData()
        self.chart.set_time_scale(scale)

    def _on_display_toggled(self):
        self.chart.set_display_options(
            self.cb_today.isChecked(),
            self.cb_inazuma.isChecked()
        )

    def sync_vertical_scroll(self, value):
        """Sync vertical scroll with task table, offset by header height."""
        self.chart.verticalScrollBar().setValue(value)
