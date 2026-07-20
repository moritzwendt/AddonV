from __future__ import annotations

import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from backend import Backend


def _asset_path(name: str) -> str:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


def _set_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AddonV.App")
    except Exception:
        pass


def _apply_dark_palette(app: QApplication) -> None:
    p = app.palette()
    p.setColor(QPalette.Window, QColor(27, 28, 31))
    p.setColor(QPalette.WindowText, QColor(230, 230, 230))
    p.setColor(QPalette.Base, QColor(23, 24, 27))
    p.setColor(QPalette.Text, QColor(230, 230, 230))
    p.setColor(QPalette.Button, QColor(42, 44, 49))
    p.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    p.setColor(QPalette.Highlight, QColor(90, 168, 50))
    p.setColor(QPalette.ToolTipBase, QColor(35, 36, 40))
    p.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    app.setPalette(p)


def run() -> None:
    _set_windows_app_id()
    app = QApplication(sys.argv)
    _apply_dark_palette(app)
    icon_path = _asset_path("logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    backend = Backend()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(_asset_path(os.path.join("qml", "Main.qml"))))
    if not engine.rootObjects():
        sys.exit("Failed to load QML UI")

    sys.exit(app.exec())


if __name__ == "__main__":
    run()
