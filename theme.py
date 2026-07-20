from __future__ import annotations

BG = "#1b1c1f"
PANEL = "#232428"
PANEL2 = "#2a2c31"
FIELD = "#17181b"
BORDER = "#34363c"
HOVER = "#303237"
TEXT = "#e6e6e6"
MUTED = "#9aa0a6"

ACCENT_PRESETS = ["#3e96ea", "#36ac62", "#957ee5", "#df911a", "#e45d84", "#00b1ad"]


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lighten(hex_color: str, amount: float) -> str:
    r, g, b = _rgb(hex_color)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = _rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"


def build_qss(accent: str) -> str:
    accent_hover = _lighten(accent, 0.15)
    accent_dim = _rgba(accent, 0.22)
    return f"""
    * {{ color: {TEXT}; font-size: 13px; }}
    QWidget#Container {{ background: {BG}; border-radius: 14px; }}
    QFrame#Sidebar {{ background: {PANEL}; border-radius: 12px; }}
    QWidget#TitleBar, QWidget#Page, QStackedWidget {{ background: transparent; }}

    QLabel#PageTitle {{ font-size: 20px; font-weight: 700; color: {TEXT}; }}
    QLabel#Version {{ color: {MUTED}; font-size: 11px; }}
    QLabel#SectionLabel {{ color: {MUTED}; font-size: 11px; font-weight: 600; }}

    QPushButton#TabButton {{
        text-align: left; padding: 9px 12px; border-radius: 9px;
        background: transparent; border: none; font-weight: 600; color: {TEXT};
    }}
    QPushButton#TabButton:hover {{ background: {HOVER}; }}
    QPushButton#TabButton:checked {{ background: {accent}; color: #ffffff; }}

    QPushButton#Hamburger {{
        background: transparent; border: none; border-radius: 8px;
        padding: 6px; font-size: 16px; color: {TEXT};
    }}
    QPushButton#Hamburger:hover {{ background: {HOVER}; }}

    QPushButton {{
        background: {PANEL2}; color: {TEXT}; border: 1px solid {BORDER};
        border-radius: 9px; padding: 7px 14px;
    }}
    QPushButton:hover {{ background: {HOVER}; }}
    QPushButton:disabled {{ color: #6b6e74; background: {PANEL}; }}
    QPushButton#Primary {{ background: {accent}; border: none; color: #ffffff; font-weight: 600; }}
    QPushButton#Primary:hover {{ background: {accent_hover}; }}

    QPushButton#WinBtn {{
        background: transparent; border: none; border-radius: 7px;
        padding: 3px 9px; color: {MUTED}; font-size: 13px;
    }}
    QPushButton#WinBtn:hover {{ background: {HOVER}; color: {TEXT}; }}
    QPushButton#WinBtn[close="true"]:hover {{ background: #e0443b; color: #ffffff; }}

    QLineEdit, QComboBox {{
        background: {FIELD}; border: 1px solid {BORDER}; border-radius: 8px;
        padding: 6px 10px; color: {TEXT}; selection-background-color: {accent};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {accent}; }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background: {FIELD}; border: 1px solid {BORDER};
        selection-background-color: {accent}; outline: 0;
    }}

    QListWidget {{
        background: {FIELD}; border: 1px solid {BORDER};
        border-radius: 10px; outline: 0;
    }}
    QListWidget::item {{ border-bottom: 1px solid #26282d; }}
    QListWidget::item:selected {{ background: {accent_dim}; }}

    QCheckBox {{ spacing: 8px; }}
    QCheckBox::indicator {{
        width: 18px; height: 18px; border: 1px solid {BORDER};
        border-radius: 5px; background: {FIELD};
    }}
    QCheckBox::indicator:checked {{ background: {accent}; border: 1px solid {accent}; }}

    QTextEdit#Terminal {{
        background: #141517; border: 1px solid {BORDER}; border-radius: 10px;
        font-family: Consolas, 'Courier New', monospace; font-size: 12px; color: {TEXT};
    }}

    QFrame#Card {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 12px; }}

    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: #3a3d44; border-radius: 5px; min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: #4a4e56; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    """
