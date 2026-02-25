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
DARK_COLORS = {
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

ENERGETIC_COLORS = {
    "bg_primary": "#fff5e6",
    "bg_secondary": "#ffe4b5",
    "bg_header": "#ff8c00",
    "bg_hover": "#ffa07a",
    "accent": "#ff4500",
    "accent_light": "#ff7f50",
    "accent_gradient_start": "#ffd700",
    "accent_gradient_end": "#ff8c00",
    "critical": "#dc143c",
    "critical_dark": "#b22222",
    "milestone": "#ff6347",
    "summary_bar": "#32cd32",
    "progress": "#ff4500",
    "text_primary": "#4a2511",
    "text_secondary": "#8b4513",
    "text_muted": "#a0522d",
    "border": "#f4a460",
    "border_light": "#ffdab9",
    "grid_line": "#ffdead",
    "selection": "#ffb6c1",
    "today_line": "#ff0000",
    "weekend_bg": "#ffefd5",
    "gantt_bg": "#ffffff",
    "gantt_header_bg": "#ffd700",
    "dependency_arrow": "#ff4500",
    "baseline": "#cd853f",
}

COLORS = DARK_COLORS.copy()

def get_energetic_theme_stylesheet() -> str:
    """Return the energetic theme QSS stylesheet."""
    return """
    /* ===== Global Energetic ===== */
    * {
        font-family: "Segoe UI", "Yu Gothic UI", "Meiryo UI", sans-serif;
        font-size: 13px;
        font-weight: 600;
    }

    QMainWindow {
        background-color: #fff5e6;
    }

    QWidget {
        background-color: #fff5e6;
        color: #4a2511;
    }

    /* ===== Menu Bar ===== */
    QMenuBar {
        background-color: #ff8c00;
        color: #ffffff;
        border-bottom: 2px solid #f4a460;
        padding: 4px;
    }
    QMenuBar::item:selected {
        background-color: #ff4500;
        border-radius: 4px;
    }
    QMenu {
        background-color: #ffe4b5;
        border: 2px solid #f4a460;
        border-radius: 6px;
        padding: 6px;
    }
    QMenu::item {
        color: #4a2511;
    }
    QMenu::item:selected {
        background-color: #ff4500;
        color: #ffffff;
    }

    /* ===== Toolbar ===== */
    QToolBar {
        background-color: #ff8c00;
        border-bottom: 2px solid #f4a460;
        padding: 6px;
    }
    QToolButton {
        background-color: #ffffff;
        border: 1px solid #f4a460;
        border-radius: 4px;
        padding: 4px 6px;
        color: #4a2511;
        font-size: 12px;
        font-weight: 600;
    }
    QToolButton:hover {
        background-color: #ffe4b5;
        border-color: #ff4500;
    }
    QToolButton:pressed {
        background-color: #ffb6c1;
    }
    QToolButton:checked {
        background-color: #ff4500;
        color: #ffffff;
    }

    /* ===== Tree / Table View ===== */
    QTreeView, QTableView {
        background-color: #ffffff;
        alternate-background-color: #fff5e6;
        border: 2px solid #ffdab9;
        gridline-color: #ffdead;
        selection-background-color: #ffb6c1;
        selection-color: #b22222;
    }
    QTreeView::item, QTableView::item {
        padding: 4px 8px;
        border-bottom: 1px solid #ffdead;
        min-height: 28px;
    }
    QTreeView::item:hover, QTableView::item:hover {
        background-color: #ffe4b5;
        color: #4a2511;
    }

    QHeaderView {
        background-color: #ffd700;
    }
    QHeaderView::section {
        background-color: #ffd700;
        color: #4a2511;
        padding: 6px 8px;
        border: 1px solid #f4a460;
        font-size: 12px;
        font-weight: bold;
    }

    /* ===== Dialogs & Input ===== */
    QDialog {
        background-color: #ffe4b5;
        border: 2px solid #f4a460;
        border-radius: 8px;
    }
    QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
        background-color: #ffffff;
        border: 2px solid #ffdab9;
        border-radius: 4px;
        padding: 4px 8px;
        color: #4a2511;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
        border-color: #ff4500;
    }

    /* ===== Buttons ===== */
    QPushButton {
        background-color: #ffffff;
        color: #4a2511;
        border: 2px solid #f4a460;
        border-radius: 4px;
        padding: 6px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #ffe4b5;
        border-color: #ff4500;
    }
    QPushButton:pressed {
        background-color: #ff8c00;
        color: #ffffff;
    }
    QPushButton[primary="true"] {
        background-color: #ff4500;
        color: #ffffff;
        border-color: #b22222;
    }

    /* ===== Tab Widget ===== */
    QTabWidget::pane {
        border: 2px solid #ffdab9;
        border-radius: 4px;
        background-color: #ffffff;
    }
    QTabBar::tab {
        background-color: #ffd700;
        color: #4a2511;
        padding: 8px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background-color: #ff4500;
        color: #ffffff;
        border: 2px solid #f4a460;
        border-bottom: none;
    }

    /* ===== CheckBox ===== */
    QCheckBox {
        color: #4a2511;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #f4a460;
        border-radius: 4px;
        background-color: #ffffff;
    }
    QCheckBox::indicator:checked {
        background-color: #ff4500;
        border-color: #ff4500;
    }
    """

def apply_theme(app, theme_name="dark"):
    global COLORS
    if theme_name == "energetic":
        COLORS.update(ENERGETIC_COLORS)
        app.setStyleSheet(get_energetic_theme_stylesheet())
    else:
        COLORS.update(DARK_COLORS)
        app.setStyleSheet(get_theme_stylesheet())
