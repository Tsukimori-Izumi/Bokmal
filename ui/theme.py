"""Dark theme QSS stylesheet for UniTK."""


def get_theme_stylesheet() -> str:
    """Return the dark theme QSS stylesheet."""
    return """
    /* ===== Global ===== */
    * {
        font-family: "Segoe UI", "Yu Gothic UI", "Meiryo UI", sans-serif;
        font-size: 13px;
    }

    QMainWindow {
        background-color: #1a1b2e;
    }

    QWidget {
        background-color: #1a1b2e;
        color: #e0e0e8;
    }

    /* ===== Menu Bar ===== */
    QMenuBar {
        background-color: #12132a;
        color: #c0c0d0;
        border-bottom: 1px solid #2a2b4a;
        padding: 2px;
    }
    QMenuBar::item {
        padding: 6px 12px;
        border-radius: 4px;
    }
    QMenuBar::item:selected {
        background-color: #3a3b6e;
    }
    QMenu {
        background-color: #1e1f3a;
        border: 1px solid #3a3b6e;
        border-radius: 6px;
        padding: 4px;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #4a4bae;
    }
    QMenu::separator {
        height: 1px;
        background-color: #2a2b4a;
        margin: 4px 8px;
    }

    /* ===== Toolbar ===== */
    QToolBar {
        background-color: #12132a;
        border-bottom: 1px solid #2a2b4a;
        padding: 4px 8px;
        spacing: 4px;
    }
    QToolBar::separator {
        width: 1px;
        background-color: #2a2b4a;
        margin: 4px 6px;
    }
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px 10px;
        color: #c0c0d0;
        font-size: 12px;
    }
    QToolButton:hover {
        background-color: #2a2b5e;
        border-color: #4a4bae;
    }
    QToolButton:pressed {
        background-color: #3a3b7e;
    }
    QToolButton:checked {
        background-color: #4a4bae;
        color: #ffffff;
    }

    /* ===== Splitter ===== */
    QSplitter::handle {
        background-color: #2a2b4a;
        width: 3px;
    }
    QSplitter::handle:hover {
        background-color: #6c6cff;
    }

    /* ===== Tree / Table View ===== */
    QTreeView, QTableView {
        background-color: #14152e;
        alternate-background-color: #181936;
        border: none;
        gridline-color: #2a2b4a;
        selection-background-color: #3a3b8e;
        selection-color: #ffffff;
        outline: none;
    }
    QTreeView::item, QTableView::item {
        padding: 4px 8px;
        border-bottom: 1px solid #1e1f3e;
        min-height: 26px;
    }
    QTreeView::item:hover, QTableView::item:hover {
        background-color: #22234a;
    }
    QTreeView::item:selected, QTableView::item:selected {
        background-color: #3a3b8e;
    }
    QTreeView::branch {
        background-color: transparent;
    }
    QTreeView::branch:has-children:!has-siblings:closed,
    QTreeView::branch:closed:has-children:has-siblings {
        image: none;
        border-image: none;
    }
    QTreeView::branch:open:has-children:!has-siblings,
    QTreeView::branch:open:has-children:has-siblings {
        image: none;
        border-image: none;
    }

    /* ===== Header View ===== */
    QHeaderView {
        background-color: #12132a;
        border: none;
    }
    QHeaderView::section {
        background-color: #1a1b3e;
        color: #a0a0c0;
        padding: 6px 8px;
        border: none;
        border-right: 1px solid #2a2b4a;
        border-bottom: 1px solid #2a2b4a;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    QHeaderView::section:hover {
        background-color: #22234a;
        color: #d0d0e8;
    }

    /* ===== ScrollBar ===== */
    QScrollBar:vertical {
        background-color: #14152e;
        width: 10px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #3a3b6e;
        border-radius: 5px;
        min-height: 30px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #5a5bae;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #14152e;
        height: 10px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background-color: #3a3b6e;
        border-radius: 5px;
        min-width: 30px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #5a5bae;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    /* ===== Status Bar ===== */
    QStatusBar {
        background-color: #0e0f24;
        color: #8080a0;
        border-top: 1px solid #2a2b4a;
        padding: 2px 8px;
        font-size: 11px;
    }

    /* ===== Dialogs & Input ===== */
    QDialog {
        background-color: #1a1b3e;
        border: 1px solid #3a3b6e;
        border-radius: 8px;
    }
    QLineEdit {
        background-color: #14152e;
        border: 1px solid #2a2b5e;
        border-radius: 4px;
        padding: 6px 8px;
        color: #e0e0e8;
        selection-background-color: #4a4bae;
    }
    QLineEdit:focus {
        border-color: #6c6cff;
    }
    QSpinBox, QDoubleSpinBox, QDateEdit {
        background-color: #14152e;
        border: 1px solid #2a2b5e;
        border-radius: 4px;
        padding: 4px 8px;
        color: #e0e0e8;
    }
    QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
        border-color: #6c6cff;
    }
    QComboBox {
        background-color: #14152e;
        border: 1px solid #2a2b5e;
        border-radius: 4px;
        padding: 4px 8px;
        color: #e0e0e8;
        min-width: 80px;
    }
    QComboBox:hover {
        border-color: #4a4bae;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: #1e1f3a;
        border: 1px solid #3a3b6e;
        selection-background-color: #4a4bae;
    }

    /* ===== Buttons ===== */
    QPushButton {
        background-color: #3a3b7e;
        color: #e0e0f0;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #4a4bae;
    }
    QPushButton:pressed {
        background-color: #5a5bbe;
    }
    QPushButton:disabled {
        background-color: #2a2b4a;
        color: #606080;
    }
    QPushButton[primary="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #6c6cff, stop:1 #8a6cff);
    }
    QPushButton[primary="true"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #7c7cff, stop:1 #9a7cff);
    }

    /* ===== Tab Widget ===== */
    QTabWidget::pane {
        border: 1px solid #2a2b4a;
        border-radius: 4px;
        background-color: #1a1b3e;
    }
    QTabBar::tab {
        background-color: #14152e;
        color: #8080a0;
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid transparent;
    }
    QTabBar::tab:hover {
        color: #c0c0e0;
        background-color: #1e1f3e;
    }
    QTabBar::tab:selected {
        color: #ffffff;
        border-bottom: 2px solid #6c6cff;
    }

    /* ===== Progress Bar ===== */
    QProgressBar {
        background-color: #14152e;
        border: none;
        border-radius: 3px;
        height: 6px;
        text-align: center;
        font-size: 10px;
        color: transparent;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #4a8cff, stop:1 #6c6cff);
        border-radius: 3px;
    }

    /* ===== Label ===== */
    QLabel {
        color: #c0c0d0;
        background: transparent;
    }
    QLabel[heading="true"] {
        font-size: 16px;
        font-weight: 700;
        color: #e0e0f0;
    }

    /* ===== CheckBox ===== */
    QCheckBox {
        color: #c0c0d0;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #3a3b6e;
        border-radius: 3px;
        background-color: #14152e;
    }
    QCheckBox::indicator:checked {
        background-color: #6c6cff;
        border-color: #6c6cff;
    }

    /* ===== ToolTip ===== */
    QToolTip {
        background-color: #1e1f3a;
        color: #e0e0f0;
        border: 1px solid #4a4bae;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
    }

    /* ===== Group Box ===== */
    QGroupBox {
        border: 1px solid #2a2b4a;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 16px;
        font-weight: 600;
        color: #a0a0c0;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: #a0a0c0;
    }
    """


# Color constants used in Python code
COLORS = {
    "bg_primary": "#1a1b2e",
    "bg_secondary": "#14152e",
    "bg_header": "#12132a",
    "bg_hover": "#22234a",
    "accent": "#6c6cff",
    "accent_light": "#8a8aff",
    "accent_gradient_start": "#4a8cff",
    "accent_gradient_end": "#6c6cff",
    "critical": "#ff6b6b",
    "critical_dark": "#cc4444",
    "milestone": "#ffd700",
    "summary_bar": "#8888cc",
    "progress": "#4a8cff",
    "text_primary": "#e0e0e8",
    "text_secondary": "#a0a0c0",
    "text_muted": "#606080",
    "border": "#2a2b4a",
    "border_light": "#3a3b6e",
    "grid_line": "#1e1f3e",
    "selection": "#3a3b8e",
    "today_line": "#ff6b6b",
    "weekend_bg": "#111225",
    "gantt_bg": "#14152e",
    "gantt_header_bg": "#1a1b3e",
    "dependency_arrow": "#8888bb",
    "baseline": "#555577",
}
