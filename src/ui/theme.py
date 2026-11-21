THEMES = {
    "light": {
        "bg": "#f4f6fb",
        "panel": "#ffffff",
        "panel_alt": "#eef1f8",
        "border": "#d8ddea",
        "text": "#1c2333",
        "text_dim": "#6b7386",
        "accent": "#4a6cf7",
        "accent_hover": "#3a56d4",
        "accent_soft": "#e3e9ff",
        "green": "#2fa871",
        "red": "#e05555",
        "orange": "#e8912d",
        "purple": "#8b5cf6",
        "canvas": "#ffffff",
        "grid": "#e6eaf4",
        "shadow": "rgba(30,40,80,0.12)",
    },
    "dark": {
        "bg": "#141824",
        "panel": "#1e2332",
        "panel_alt": "#262c3d",
        "border": "#353d52",
        "text": "#e8ecf6",
        "text_dim": "#9aa3ba",
        "accent": "#6d8bff",
        "accent_hover": "#8aa4ff",
        "accent_soft": "#2b3566",
        "green": "#4fd39a",
        "red": "#ff6b6b",
        "orange": "#f5a94c",
        "purple": "#a98bff",
        "canvas": "#191e2b",
        "grid": "#2a3145",
        "shadow": "rgba(0,0,0,0.4)",
    },
}

CURRENT = "light"


def theme():
    return THEMES[CURRENT]


def set_theme(name):
    global CURRENT
    if name in THEMES:
        CURRENT = name
    return theme()


def qss(name=None):
    t = THEMES[name or CURRENT]
    return f"""
    QWidget {{
        background: {t['bg']};
        color: {t['text']};
        font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
        font-size: 13px;
    }}
    QMainWindow, QDialog {{ background: {t['bg']}; }}
    QFrame, QGroupBox {{
        background: {t['panel']};
        border: 1px solid {t['border']};
        border-radius: 8px;
    }}
    QGroupBox {{ font-weight: bold; margin-top: 12px; padding-top: 18px; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; color: {t['accent']}; }}
    QPushButton {{
        background: {t['panel_alt']};
        color: {t['text']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 7px 14px;
    }}
    QPushButton:hover {{ background: {t['accent_soft']}; border-color: {t['accent']}; }}
    QPushButton:pressed {{ background: {t['accent']}; color: #ffffff; }}
    QPushButton:checked {{ background: {t['accent']}; color: #ffffff; border-color: {t['accent']}; }}
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit {{
        background: {t['panel']};
        color: {t['text']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 5px 8px;
        selection-background-color: {t['accent']};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{ border-color: {t['accent']}; }}
    QSlider::groove:horizontal {{ background: {t['border']}; height: 6px; border-radius: 3px; }}
    QSlider::handle:horizontal {{ background: {t['accent']}; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }}
    QTabWidget::pane {{ border: 1px solid {t['border']}; border-radius: 8px; background: {t['panel']}; }}
    QTabBar::tab {{
        background: {t['panel_alt']}; color: {t['text_dim']};
        padding: 8px 18px; border: 1px solid {t['border']};
        border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{ background: {t['panel']}; color: {t['accent']}; font-weight: bold; }}
    QListWidget, QTreeWidget, QTableWidget {{
        background: {t['panel']}; color: {t['text']};
        border: 1px solid {t['border']}; border-radius: 8px;
    }}
    QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
        background: {t['accent_soft']}; color: {t['text']};
    }}
    QScrollBar:vertical {{ background: transparent; width: 12px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 6px; min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: {t['text_dim']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QLabel {{ background: transparent; }}
    QToolTip {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['accent']}; padding: 4px; }}
    QMenuBar {{ background: {t['panel']}; }}
    QMenu {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; }}
    QMenu::item:selected {{ background: {t['accent']}; color: #ffffff; }}
    QStatusBar {{ background: {t['panel']}; color: {t['text_dim']}; }}
    """
