from datetime import date, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from ui.theme import COLORS


class BurndownScene(QGraphicsScene):
    """Custom scene for drawing the burndown chart."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor(COLORS["gantt_bg"])))
        self._tasks: list[dict] = []
        self._margin = 50

    def draw_chart(self, tasks: list[dict]):
        self.clear()
        self._tasks = tasks

        if not tasks:
            return

        # Find project boundaries
        starts = [t["start_date"] for t in tasks if t.get("start_date")]
        ends = [t["end_date"] for t in tasks if t.get("end_date")]
        
        if not starts or not ends:
            return

        p_start = min(starts)
        p_end = max(ends)
        total_days = (p_end - p_start).days
        if total_days <= 0:
            total_days = 1

        # Calculate total "points" (using duration as points)
        total_duration = sum(t.get("duration", 0) for t in tasks if not t.get("is_summary") and not t.get("is_milestone"))
        if total_duration == 0:
            total_duration = 1

        # Calculate current remaining work
        completed_duration = 0.0
        for t in tasks:
            if not t.get("is_summary") and not t.get("is_milestone"):
                dur = t.get("duration", 0)
                prog = t.get("progress", 0) / 100.0
                completed_duration += dur * prog
        
        remaining_work = total_duration - completed_duration

        # Dimensions
        w = 800
        h = 400
        self.setSceneRect(0, 0, w, h)

        plot_rect = QRectF(self._margin, self._margin, w - 2 * self._margin, h - 2 * self._margin)

        # Draw Grid
        grid_pen = QPen(QColor(COLORS["grid_line"]), 1)
        
        # Horizontal lines (Work)
        for i in range(6):
            y = plot_rect.bottom() - (plot_rect.height() * i / 5)
            line = self.addLine(plot_rect.left(), y, plot_rect.right(), y, grid_pen)
            line.setZValue(-1)
            
            # Y-axis labels
            val = int(total_duration * i / 5)
            text = self.addText(f"{val}日", QFont("Segoe UI", 9))
            text.setDefaultTextColor(QColor(COLORS["text_secondary"]))
            text.setPos(plot_rect.left() - 40, y - 10)

        # Vertical lines (Time)
        for i in range(6):
            x = plot_rect.left() + (plot_rect.width() * i / 5)
            line = self.addLine(x, plot_rect.top(), x, plot_rect.bottom(), grid_pen)
            line.setZValue(-1)

            # X-axis labels
            d = p_start + timedelta(days=int(total_days * i / 5))
            text = self.addText(d.strftime("%m/%d"), QFont("Segoe UI", 9))
            text.setDefaultTextColor(QColor(COLORS["text_secondary"]))
            text.setPos(x - 15, plot_rect.bottom() + 10)

        # Draw Ideal Line
        ideal_pen = QPen(QColor(COLORS["border_light"]), 2, Qt.PenStyle.DashLine)
        self.addLine(
            plot_rect.left(), plot_rect.top(),
            plot_rect.right(), plot_rect.bottom(),
            ideal_pen
        )

        # Draw Actual "Today" Point/Line
        today = date.today()
        if today < p_start:
            today = p_start
        elif today > p_end:
            today = p_end
            
        today_ratio = (today - p_start).days / total_days
        today_x = plot_rect.left() + plot_rect.width() * today_ratio
        
        # Calculate Y for remaining work
        rem_ratio = remaining_work / total_duration
        rem_y = plot_rect.bottom() - (plot_rect.height() * rem_ratio)

        # Draw actual progress line from start to today
        actual_pen = QPen(QColor(COLORS["accent"]), 3)
        self.addLine(
            plot_rect.left(), plot_rect.top(),
            today_x, rem_y,
            actual_pen
        )

        # Draw point at today
        self.addEllipse(today_x - 4, rem_y - 4, 8, 8, Qt.PenStyle.NoPen, QBrush(QColor(COLORS["accent_light"])))
        
        # Label remaining work
        lbl = self.addText(f"残: {remaining_work:.1f}日", QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setDefaultTextColor(QColor(COLORS["accent_light"]))
        lbl.setPos(today_x + 5, rem_y - 20)


class BurndownChartView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = BurndownScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    def load_tasks(self, tasks: list[dict]):
        self._scene.draw_chart(tasks)


class BurndownWidget(QWidget):
    """Container for the burndown chart."""

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

        title = QLabel("📉 バーンダウンチャート (残作業日数)")
        title.setStyleSheet(f"color: {COLORS['accent_light']}; font-weight: bold;")
        h_layout.addWidget(title)
        
        legend_ideal = QLabel("--- 理想線")
        legend_ideal.setStyleSheet(f"color: {COLORS['border_light']}; font-size: 11px;")
        h_layout.addWidget(legend_ideal)
        
        legend_actual = QLabel("— 実績(推計)")
        legend_actual.setStyleSheet(f"color: {COLORS['accent']}; font-size: 11px;")
        h_layout.addWidget(legend_actual)
        
        h_layout.addStretch()
        layout.addWidget(header)

        self.chart = BurndownChartView(self)
        layout.addWidget(self.chart)

    def load_tasks(self, tasks: list[dict]):
        self.chart.load_tasks(tasks)
