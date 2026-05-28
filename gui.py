"""Main GUI window built with PySide6."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPalette, QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

import dlclist
import i18n
from config import Config
from gta_detect import derive_paths, find_default_install, is_gta_root
from i18n import LANGUAGES, T
from installers import install_dlc, install_els


def _asset_path(name: str) -> str:
    """Resolve a bundled asset both in dev mode and inside a PyInstaller build.

    PyInstaller onedir puts datas next to the exe; onefile extracts to
    `sys._MEIPASS`. In dev mode, assets live next to this source file.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


def _system_default_language() -> str:
    """Map the OS locale to one of our supported languages, fallback to English."""
    name = QLocale.system().name().lower()  # e.g. "de_de"
    code = name.split("_", 1)[0]
    return code if code in LANGUAGES else "en"


class LanguageDialog(QDialog):
    """Simple radio-button picker shown on first run or via the language button."""

    def __init__(self, current: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("lang_dialog_title"))
        self.setModal(True)
        self._chosen = current

        layout = QVBoxLayout(self)
        hint = QLabel(T("lang_dialog_hint"))
        hint.setStyleSheet("color: #ddd;")
        layout.addWidget(hint)

        self._group = QButtonGroup(self)
        for code, label in LANGUAGES.items():
            rb = QRadioButton(label)
            rb.setProperty("lang_code", code)
            if code == current:
                rb.setChecked(True)
            self._group.addButton(rb)
            layout.addWidget(rb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.button(QDialogButtonBox.Ok).setText(T("ok"))
        buttons.button(QDialogButtonBox.Cancel).setText(T("cancel"))
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        btn = self._group.checkedButton()
        if btn is not None:
            self._chosen = str(btn.property("lang_code"))
        self.accept()

    def chosen(self) -> str:
        return self._chosen


class DropZone(QFrame):
    """A labelled drop target that calls back with each dropped path."""

    BASE_STYLE = """
        QFrame {
            background-color: #2b2b2e;
            border: 2px dashed #555;
            border-radius: 10px;
        }
    """
    HOVER_STYLE = """
        QFrame {
            background-color: #2d3e50;
            border: 2px dashed #3498db;
            border-radius: 10px;
        }
    """

    def __init__(self, title: str, hint: str, on_drop):
        super().__init__()
        self._on_drop = on_drop
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setStyleSheet(self.BASE_STYLE)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #f0f0f0; border: 0;")
        self.title_lbl.setAlignment(Qt.AlignCenter)

        self.hint_lbl = QLabel(hint)
        self.hint_lbl.setStyleSheet("color: #b0b0b0; border: 0;")
        self.hint_lbl.setAlignment(Qt.AlignCenter)
        self.hint_lbl.setWordWrap(True)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.hint_lbl)

    def set_texts(self, title: str, hint: str) -> None:
        self.title_lbl.setText(title)
        self.hint_lbl.setText(hint)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.HOVER_STYLE)

    def dragLeaveEvent(self, event) -> None:
        self.setStyleSheet(self.BASE_STYLE)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setStyleSheet(self.BASE_STYLE)
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                self._on_drop(Path(local))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self._init_language()

        self.resize(960, 680)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)

        # --- Logo header ------------------------------------------------
        logo_path = _asset_path("logo.png")
        if os.path.exists(logo_path):
            logo_lbl = QLabel()
            pixmap = QPixmap(logo_path)
            logo_lbl.setPixmap(
                pixmap.scaledToHeight(96, Qt.SmoothTransformation)
            )
            logo_lbl.setAlignment(Qt.AlignCenter)
            root_layout.addWidget(logo_lbl)

        # --- GTA path row -----------------------------------------------
        path_row = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setStyleSheet("color: #ddd;")
        self.choose_btn = QPushButton()
        self.choose_btn.clicked.connect(self.choose_gta_path)
        self.lang_btn = QPushButton()
        self.lang_btn.clicked.connect(self.choose_language)
        path_row.addWidget(self.path_label, stretch=1)
        path_row.addWidget(self.choose_btn)
        path_row.addWidget(self.lang_btn)
        root_layout.addLayout(path_row)

        # --- Install-mode row ------------------------------------------
        mode_row = QHBoxLayout()
        self.mods_checkbox = QCheckBox()
        self.mods_checkbox.setChecked(self.config.use_mods_folder)
        self.mods_checkbox.toggled.connect(self.on_mods_toggle)
        self.mode_status = QLabel()
        self.mode_status.setStyleSheet("color: #b0b0b0;")
        mode_row.addWidget(self.mods_checkbox)
        mode_row.addStretch(1)
        mode_row.addWidget(self.mode_status)
        root_layout.addLayout(mode_row)

        # --- Drop zones -------------------------------------------------
        grid = QGridLayout()
        grid.setSpacing(12)
        self.zone_dlc = DropZone(T("dlc_zone_title"), T("dlc_zone_hint"), self.on_dlc_drop)
        self.zone_els = DropZone(T("els_zone_title"), T("els_zone_hint"), self.on_els_drop)
        grid.addWidget(self.zone_dlc, 0, 0)
        grid.addWidget(self.zone_els, 0, 1)
        root_layout.addLayout(grid)

        # --- dlclist.xml row -------------------------------------------
        xml_row = QHBoxLayout()
        self.xml_label = QLabel()
        self.xml_label.setStyleSheet("color: #ddd;")
        self.xml_btn = QPushButton()
        self.xml_btn.clicked.connect(self.choose_dlclist_xml)
        self.clear_xml_btn = QPushButton()
        self.clear_xml_btn.clicked.connect(self.clear_dlclist_xml)
        xml_row.addWidget(self.xml_label, stretch=1)
        xml_row.addWidget(self.xml_btn)
        xml_row.addWidget(self.clear_xml_btn)
        root_layout.addLayout(xml_row)

        # --- Log --------------------------------------------------------
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "background-color: #181818; color: #ddd; "
            "font-family: Consolas, 'Courier New', monospace; font-size: 12px;"
        )
        root_layout.addWidget(self.log, stretch=1)

        self._apply_dark_palette()
        self.retranslate_ui()
        self._first_run_autodetect()

    # ----- language ----- #
    def _init_language(self) -> None:
        saved = self.config.language
        if saved and saved in LANGUAGES:
            i18n.set_language(saved)
            return
        # First run: pick the system default, but require explicit confirmation.
        i18n.set_language(_system_default_language())
        dlg = LanguageDialog(i18n.get_language(), parent=self)
        dlg.exec()
        i18n.set_language(dlg.chosen())
        self.config.language = i18n.get_language()
        self.config.save()

    def choose_language(self) -> None:
        dlg = LanguageDialog(i18n.get_language(), parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        new_lang = dlg.chosen()
        if new_lang == i18n.get_language():
            return
        i18n.set_language(new_lang)
        self.config.language = new_lang
        self.config.save()
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(T("window_title"))
        self.choose_btn.setText(T("choose_gta_btn"))
        self.lang_btn.setText(T("lang_button"))
        self.mods_checkbox.setText(T("mods_checkbox"))
        self.zone_dlc.set_texts(T("dlc_zone_title"), T("dlc_zone_hint"))
        self.zone_els.set_texts(T("els_zone_title"), T("els_zone_hint"))
        self.xml_btn.setText(T("dlclist_btn"))
        self.clear_xml_btn.setText(T("dlclist_clear_btn"))
        self._refresh_labels()

    # ----- helpers ----- #
    def _apply_dark_palette(self) -> None:
        p = self.palette()
        p.setColor(QPalette.Window, QColor(40, 40, 43))
        p.setColor(QPalette.WindowText, QColor(220, 220, 220))
        p.setColor(QPalette.Base, QColor(28, 28, 30))
        p.setColor(QPalette.Text, QColor(220, 220, 220))
        p.setColor(QPalette.Button, QColor(60, 60, 64))
        p.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        self.setPalette(p)

    def _refresh_labels(self) -> None:
        if self.config.gta_path:
            self.path_label.setText(T("gta_path_label", path=self.config.gta_path))
        else:
            self.path_label.setText(T("gta_path_unset"))
        if self.config.dlclist_xml_path:
            self.xml_label.setText(T("dlclist_label", path=self.config.dlclist_xml_path))
        else:
            self.xml_label.setText(T("dlclist_unset"))
        if self.config.use_mods_folder:
            self.mode_status.setText(T("mode_safe"))
            self.mode_status.setStyleSheet("color: #6fbf73;")
        else:
            self.mode_status.setText(T("mode_direct"))
            self.mode_status.setStyleSheet("color: #e07a5f; font-weight: 600;")

    def _first_run_autodetect(self) -> None:
        if self.config.gta_path:
            return
        default = find_default_install()
        if default:
            self.config.gta_path = str(default)
            self.config.save()
            self._refresh_labels()
            self.log_msg(T("gta_detected", path=str(default)))
        else:
            self.log_msg(T("gta_not_detected"))

    def log_msg(self, msg: str) -> None:
        self.log.appendPlainText(msg)

    def _ensure_paths(self):
        gta = self.config.gta_path
        if not gta or not is_gta_root(Path(gta)):
            QMessageBox.warning(self, T("gta_missing_title"), T("gta_missing_body"))
            return None
        return derive_paths(Path(gta), use_mods=self.config.use_mods_folder)

    # ----- button actions ----- #
    def choose_gta_path(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, T("choose_gta_dialog"))
        if not chosen:
            return
        path = Path(chosen)
        if not is_gta_root(path):
            QMessageBox.warning(self, T("invalid_folder_title"), T("invalid_folder_body"))
            return
        self.config.gta_path = str(path)
        self.config.save()
        self._refresh_labels()
        self.log_msg(T("gta_path_set", path=str(path)))

    def choose_dlclist_xml(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, T("choose_dlclist_dialog"), "", "XML (*.xml)"
        )
        if not path:
            return
        self.config.dlclist_xml_path = path
        self.config.save()
        self._refresh_labels()
        self.log_msg(T("dlclist_set", path=path))

    def clear_dlclist_xml(self) -> None:
        self.config.dlclist_xml_path = ""
        self.config.save()
        self._refresh_labels()

    def on_mods_toggle(self, checked: bool) -> None:
        if not checked:
            reply = QMessageBox.warning(
                self,
                T("direct_warning_title"),
                T("direct_warning_body"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                self.mods_checkbox.blockSignals(True)
                self.mods_checkbox.setChecked(True)
                self.mods_checkbox.blockSignals(False)
                return
            self.log_msg(T("direct_enabled"))
        else:
            self.log_msg(T("safe_enabled"))
        self.config.use_mods_folder = checked
        self.config.save()
        self._refresh_labels()

    # ----- drop callbacks ----- #
    def on_dlc_drop(self, src: Path) -> None:
        paths = self._ensure_paths()
        if not paths:
            return
        result = install_dlc(src, paths["dlcpacks"], self.log_msg)
        self.log_msg(("[OK] " if result.ok else "[!!] ") + result.message)
        if result.ok and result.dlc_name:
            self._handle_dlclist_update(result.dlc_name)

    def on_els_drop(self, src: Path) -> None:
        paths = self._ensure_paths()
        if not paths:
            return
        target = paths["root"] / "ELS" / "pack_default"
        result = install_els(src, target, self.log_msg)
        self.log_msg(("[OK] " if result.ok else "[!!] ") + result.message)

    # ----- dlclist.xml handling ----- #
    def _handle_dlclist_update(self, dlc_name: str) -> None:
        xml = self.config.dlclist_xml_path
        if xml and Path(xml).is_file():
            try:
                changed = dlclist.update_file(Path(xml), dlc_name)
            except Exception as exc:
                self.log_msg(T("dlclist_error", err=str(exc)))
                return
            if changed:
                self.log_msg(T("dlclist_added", name=dlc_name))
            else:
                self.log_msg(T("dlclist_existed", name=dlc_name))
            return
        entry = f"    <Item>dlcpacks:/{dlc_name}/</Item>"
        self.log_msg(T("dlclist_hint_no_xml", entry=entry))


def _set_windows_app_id() -> None:
    """Tell Windows to treat AddonV as its own app in the taskbar.

    Without this, the taskbar groups under python.exe and shows its icon.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AddonV.App")
    except Exception:
        pass


def run() -> None:
    _set_windows_app_id()
    app = QApplication(sys.argv)
    icon_path = _asset_path("logo.png")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
