"""Gantt Chart Items - QGraphicsItem subclasses for gantt visualization."""

from datetime import date, timedelta

from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF, Signal, QObject
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient,
    QPolygonF, QFont, QPainterPath
)

from ui.theme import COLORS
from config import GANTT_ROW_HEIGHT


class TaskBarSignals(QObject):
    """Signals for TaskBarItem, since QGraphicsItem doesn't inherit QObject."""
    date_range_changed = Signal(int, float, float)  # task_id, new_x, new_width


class TaskBarItem(QGraphicsItem):
    """A task bar in the Gantt chart."""

    def __init__(self, task_data: dict, x: float, y: float, width: float,
                 row_height: int = GANTT_ROW_HEIGHT, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.bar_width = max(4, width)
        self.bar_height = row_height * 0.5
        self.row_height = row_height

        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.setToolTip(self._build_tooltip())

        self.setToolTip(self._build_tooltip())

        self.signals = TaskBarSignals()
        self._hovered = False
        
        # Interaction state
        self._is_resizing_left = False
        self._is_resizing_right = False
        self._drag_start_x = 0.0
        self._orig_x = x
        self._orig_width = width
        self.setAcceptDrops(False)

        # Visual handles width
        self._handle_w = 6

    def _build_tooltip(self) -> str:
        t = self.task_data
        lines = [f"タスク: {t.get('name', '')}"]
        if t.get("start_date"):
            lines.append(f"開始: {t['start_date']}")
        if t.get("end_date"):
            lines.append(f"終了: {t['end_date']}")
        lines.append(f"期間: {t.get('duration', 1)}日")
        lines.append(f"進捗: {t.get('progress', 0):.0f}%")
        if t.get("is_critical"):
            lines.append("★ クリティカルパス")
        return "\n".join(lines)

    def boundingRect(self) -> QRectF:
        return QRectF(-2, 0, self.bar_width + 4, self.row_height)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_summary = self.task_data.get("is_summary", False)
        is_milestone = self.task_data.get("is_milestone", False)
        is_critical = self.task_data.get("is_critical", False)
        progress = self.task_data.get("progress", 0) / 100.0

        y_offset = (self.row_height - self.bar_height) / 2

        if is_milestone:
            self._paint_milestone(painter, y_offset)
        elif is_summary:
            self._paint_summary(painter, y_offset)
        else:
            self._paint_normal(painter, y_offset, is_critical, progress)

        # Selection highlight
        if self.isSelected():
            painter.setPen(QPen(QColor(COLORS["accent"]), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            rect = QRectF(0, y_offset, self.bar_width, self.bar_height)
            painter.drawRoundedRect(rect, 3, 3)

    def _paint_normal(self, painter, y_offset, is_critical, progress):
        rect = QRectF(0, y_offset, self.bar_width, self.bar_height)

        # Gradient fill
        gradient = QLinearGradient(0, y_offset, 0, y_offset + self.bar_height)
        if is_critical:
            gradient.setColorAt(0, QColor(COLORS["critical"]))
            gradient.setColorAt(1, QColor(COLORS["critical_dark"]))
        else:
            gradient.setColorAt(0, QColor(COLORS["accent"]))
            gradient.setColorAt(1, QColor(COLORS["accent_gradient_start"]))

        if self._hovered:
            gradient.setColorAt(0, QColor(COLORS["accent_light"]))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 4, 4)

        # Progress fill
        if progress > 0:
            prog_width = self.bar_width * progress
            prog_rect = QRectF(0, y_offset, prog_width, self.bar_height)
            painter.setBrush(QColor(COLORS["progress"]).darker(130))
            painter.setOpacity(0.4)
            painter.drawRoundedRect(prog_rect, 4, 4)
            painter.setOpacity(1.0)

        # Progress line
        if progress > 0 and progress < 1.0:
            px = self.bar_width * progress
            painter.setPen(QPen(QColor("#ffffff"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(px, y_offset), QPointF(px, y_offset + self.bar_height))

        # Task name text (if bar is wide enough)
        if self.bar_width > 60:
            painter.setPen(QColor("#ffffff"))
            f = QFont("Segoe UI", 9)
            painter.setFont(f)
            text_rect = QRectF(4, y_offset, self.bar_width - 8, self.bar_height)
            name = self.task_data.get("name", "")
            painter.drawText(text_rect,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             name)

    def _paint_summary(self, painter, y_offset):
        """Paint summary task as a bracket bar."""
        bar_h = self.bar_height * 0.35
        y = y_offset + (self.bar_height - bar_h) / 2

        # Main bar
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["summary_bar"]))
        painter.drawRect(QRectF(0, y, self.bar_width, bar_h))

        # Left bracket
        bracket_h = self.bar_height * 0.5
        tri_left = QPolygonF([
            QPointF(0, y),
            QPointF(6, y),
            QPointF(0, y + bracket_h),
        ])
        painter.drawPolygon(tri_left)

        # Right bracket
        tri_right = QPolygonF([
            QPointF(self.bar_width, y),
            QPointF(self.bar_width - 6, y),
            QPointF(self.bar_width, y + bracket_h),
        ])
        painter.drawPolygon(tri_right)

    def _paint_milestone(self, painter, y_offset):
        """Paint milestone as a diamond."""
        size = self.bar_height * 0.5
        cx = self.bar_width / 2
        cy = y_offset + self.bar_height / 2

        diamond = QPolygonF([
            QPointF(cx, cy - size),
            QPointF(cx + size, cy),
            QPointF(cx, cy + size),
            QPointF(cx - size, cy),
        ])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["milestone"]))
        painter.drawPolygon(diamond)

        if self._hovered:
            painter.setPen(QPen(QColor("#ffffff"), 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(diamond)

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        if not self.task_data.get("is_summary") and not self.task_data.get("is_milestone"):
            pos = event.pos()
            if pos.x() <= self._handle_w:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif pos.x() >= self.bar_width - self._handle_w:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.task_data.get("is_summary") and not self.task_data.get("is_milestone"):
            pos = event.pos()
            if pos.x() <= self._handle_w:
                self._is_resizing_left = True
                self._drag_start_x = event.scenePos().x()
                self._orig_x = self.x()
                self._orig_width = self.bar_width
                event.accept()
                return
            elif pos.x() >= self.bar_width - self._handle_w:
                self._is_resizing_right = True
                self._drag_start_x = event.scenePos().x()
                self._orig_width = self.bar_width
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_resizing_left:
            dx = event.scenePos().x() - self._drag_start_x
            new_width = max(self._scene_day_width(), self._orig_width - dx)
            # Adjust x if width actually changed
            actual_dx = self._orig_width - new_width
            self.setX(self._orig_x + actual_dx)
            self.bar_width = new_width
            self.prepareGeometryChange()
            self.update()
            event.accept()
        elif self._is_resizing_right:
            dx = event.scenePos().x() - self._drag_start_x
            self.bar_width = max(self._scene_day_width(), self._orig_width + dx)
            self.prepareGeometryChange()
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_resizing_left or self._is_resizing_right:
            self._is_resizing_left = False
            self._is_resizing_right = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # Emit signal for logic layer to snap to dates
            self.signals.date_range_changed.emit(
                self.task_data["id"], self.x(), self.bar_width
            )
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _scene_day_width(self):
        """Helper to get min width (1 day)."""
        if self.scene():
            return getattr(self.scene(), "day_width", 20)
        return 20


class DependencyArrowItem(QGraphicsItem):
    """Arrow showing task dependency."""

    def __init__(self, start_point: QPointF, end_point: QPointF,
                 dep_type: str = "FS", parent=None):
        super().__init__(parent)
        self.start_point = start_point
        self.end_point = end_point
        self.dep_type = dep_type
        self._color = QColor(COLORS["dependency_arrow"])
        self._arrow_size = 6

    def boundingRect(self) -> QRectF:
        extra = self._arrow_size + 10
        return QRectF(
            min(self.start_point.x(), self.end_point.x()) - extra,
            min(self.start_point.y(), self.end_point.y()) - extra,
            abs(self.end_point.x() - self.start_point.x()) + 2 * extra,
            abs(self.end_point.y() - self.start_point.y()) + 2 * extra,
        )

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self._color, 1.5)
        painter.setPen(pen)

        sx, sy = self.start_point.x(), self.start_point.y()
        ex, ey = self.end_point.x(), self.end_point.y()

        # Draw routed path (right-angle routing)
        path = QPainterPath()
        path.moveTo(sx, sy)

        if self.dep_type == "FS":
            mid_x = sx + 10
            if mid_x < ex - 10:
                # Simple route: go right, then down/up, then right to target
                path.lineTo(mid_x, sy)
                path.lineTo(mid_x, ey)
                path.lineTo(ex, ey)
            else:
                # Need to route around
                mid_y = (sy + ey) / 2
                path.lineTo(mid_x, sy)
                path.lineTo(mid_x, mid_y)
                path.lineTo(ex - 10, mid_y)
                path.lineTo(ex - 10, ey)
                path.lineTo(ex, ey)
        else:
            # Simple direct routing for other types
            mid_y = (sy + ey) / 2
            path.lineTo(sx, mid_y)
            path.lineTo(ex, mid_y)
            path.lineTo(ex, ey)

        painter.drawPath(path)

        # Arrowhead
        arrow_p1 = QPointF(ex - self._arrow_size, ey - self._arrow_size / 2)
        arrow_p2 = QPointF(ex - self._arrow_size, ey + self._arrow_size / 2)
        arrow = QPolygonF([QPointF(ex, ey), arrow_p1, arrow_p2])
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(arrow)


class TodayLineItem(QGraphicsItem):
    """Vertical line indicating today's date."""

    def __init__(self, x: float, height: float, parent=None):
        super().__init__(parent)
        self.line_x = x
        self.line_height = height
        self.setZValue(100)

    def boundingRect(self) -> QRectF:
        return QRectF(self.line_x - 1, 0, 3, self.line_height)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(COLORS["today_line"]), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self.line_x, 0),
            QPointF(self.line_x, self.line_height)
        )
