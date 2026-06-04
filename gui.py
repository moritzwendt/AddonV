from __future__ import annotations

import html
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QPalette,
    QColor,
    QPixmap,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import archive
import dlclist
import i18n
from config import Config
from gta_detect import derive_paths, find_default_install, is_gta_root
from i18n import LANGUAGES, T
from installers import (
    closest_els_folder,
    els_has_name_collision,
    find_dlc_packs,
    find_dlc_packs_deep,
    group_els_by_folder,
    install_dlc,
    install_els,
    is_els_source,
    list_els_xmls,
    list_installed_dlc_info,
    uninstall_dlc,
)


_GROUP_COLORS = {
    "DLC": "#4aa3ff",
    "ELS": "#46c46a",
    "XML": "#e0a030",
    "INFO": "#9aa0a6",
}
_STATUS = {
    "ok":   ("✓", "#46c46a"),
    "err":  ("✗", "#e05545"),
    "work": ("→", "#9aa0a6"),
    "info": ("",       "#9aa0a6"),
}
_TEXT_COLOR = "#dddddd"
_PROGRESS_WIDTH = 24


def _asset_path(name: str) -> str:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


def _system_default_language() -> str:
    name = QLocale.system().name().lower()
    code = name.split("_", 1)[0]
    return code if code in LANGUAGES else "en"


class _ReplaceDecider:

    def __init__(
        self,
        parent,
        body_key: str,
        offer_all: bool = False,
        title_key: str = "replace_title",
    ) -> None:
        self._parent = parent
        self._body_key = body_key
        self._title_key = title_key
        self._offer_all = offer_all
        self._all: bool | None = None

    def __call__(self, name: str) -> bool:
        if self._all is not None:
            return self._all
        buttons = QMessageBox.Yes | QMessageBox.No
        if self._offer_all:
            buttons |= QMessageBox.YesToAll | QMessageBox.NoToAll
        reply = QMessageBox.question(
            self._parent,
            T(self._title_key),
            T(self._body_key, name=name),
            buttons,
            QMessageBox.No,
        )
        if reply == QMessageBox.YesToAll:
            self._all = True
            return True
        if reply == QMessageBox.NoToAll:
            self._all = False
            return False
        return reply == QMessageBox.Yes


class LanguageDialog(QDialog):

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


class SettingsDialog(QDialog):

    def __init__(self, current_lang: str, save_history: bool, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(T("settings_title"))
        self.setModal(True)

        layout = QVBoxLayout(self)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(T("settings_language")))
        self._lang_combo = QComboBox()
        for code, label in LANGUAGES.items():
            self._lang_combo.addItem(label, code)
        idx = self._lang_combo.findData(current_lang)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        lang_row.addWidget(self._lang_combo, 1)
        layout.addLayout(lang_row)

        self._history_cb = QCheckBox(T("settings_save_history"))
        self._history_cb.setChecked(save_history)
        layout.addWidget(self._history_cb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.button(QDialogButtonBox.Ok).setText(T("ok"))
        buttons.button(QDialogButtonBox.Cancel).setText(T("cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def language(self) -> str:
        return self._lang_combo.currentData()

    def save_history(self) -> bool:
        return self._history_cb.isChecked()


class DropZone(QFrame):

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
        paths = [
            Path(local)
            for url in event.mimeData().urls()
            if (local := url.toLocalFile())
        ]
        self._on_drop(paths)


class _ModRow(QWidget):

    def __init__(self, name: str, meta: str, dot_color: str, pills) -> None:
        super().__init__()
        # transparent so the list selection highlight shows through the row
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        h = QHBoxLayout(self)
        h.setContentsMargins(10, 7, 10, 7)
        h.setSpacing(10)

        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background:{dot_color}; border-radius:5px;")
        h.addWidget(dot, 0, Qt.AlignVCenter)

        col = QVBoxLayout()
        col.setSpacing(1)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            "color:#f0f0f0; font-weight:600; font-size:13px; background:transparent;"
        )
        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet("color:#8a8f94; font-size:11px; background:transparent;")
        col.addWidget(name_lbl)
        col.addWidget(meta_lbl)
        h.addLayout(col, 1)

        for text, fg, bg in pills:
            pill = QLabel(text)
            pill.setStyleSheet(
                f"color:{fg}; background:{bg}; border-radius:8px; "
                f"padding:2px 9px; font-size:11px; font-weight:600;"
            )
            h.addWidget(pill, 0, Qt.AlignVCenter)


class ManageModsDialog(QDialog):

    _ACTIVE = "active"
    _DISABLED = "disabled"
    _UNLISTED = "unlisted"

    _STATE_STYLE = {
        _ACTIVE:   ("#46c46a", "#7fe39a", "rgba(70,196,106,0.18)"),
        _DISABLED: ("#8a8f94", "#b8bdc2", "rgba(138,143,148,0.18)"),
        _UNLISTED: ("#e0a030", "#f0c060", "rgba(224,160,48,0.18)"),
    }
    _DUPLICATE_PILL = ("#ff8a7a", "rgba(224,85,69,0.22)")

    def __init__(self, dlcpacks_dir: Path, dlclist_xml: str, log_line, config, parent=None):
        super().__init__(parent)
        self._dlcpacks_dir = dlcpacks_dir
        self._dlclist_xml = dlclist_xml
        self._log_line = log_line
        self._config = config
        self._warned_dupes = False

        self.setWindowTitle(T("manage_dialog_title"))
        self.setModal(True)
        self.resize(540, 440)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText(T("manage_search_placeholder"))
        self._search.setClearButtonEnabled(True)
        self._search.setStyleSheet(
            "QLineEdit { background:#1c1c1e; color:#ddd; border:1px solid #444; "
            "border-radius:6px; padding:5px 8px; }"
        )
        self._search.textChanged.connect(self._refresh)
        self._sort_label = QLabel(T("manage_sort_label"))
        self._sort_combo = QComboBox()
        self._sort_combo.addItem(T("manage_sort_name"), "name")
        self._sort_combo.addItem(T("manage_sort_date"), "date")
        self._sort_combo.addItem(T("manage_sort_order"), "order")
        # restore the saved sort before connecting so it does not persist on init
        saved = self._sort_combo.findData(self._config.manage_sort)
        if saved >= 0:
            self._sort_combo.setCurrentIndex(saved)
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        top_row.addWidget(self._search, 1)
        top_row.addWidget(self._sort_label)
        top_row.addWidget(self._sort_combo)
        layout.addLayout(top_row)

        self._loading = False
        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { background:#1c1c1e; border:1px solid #444; "
            "border-radius:6px; outline:0; }"
            "QListWidget::item { border-bottom:1px solid #2a2a2c; }"
            "QListWidget::item:selected { background:#2d4a63; }"
        )
        self._list.itemSelectionChanged.connect(self._sync_buttons)
        self._list.model().rowsMoved.connect(self._on_rows_moved)
        layout.addWidget(self._list, 1)

        btn_row = QHBoxLayout()
        self._toggle_btn = QPushButton(T("manage_disable_btn"))
        self._toggle_btn.clicked.connect(self._toggle_selected)
        self._remove_btn = QPushButton(T("manage_remove_btn"))
        self._remove_btn.clicked.connect(self._remove_selected)
        self._repair_btn = QPushButton(T("manage_repair_btn"))
        self._repair_btn.clicked.connect(self._repair)
        close_btn = QPushButton(T("manage_close_btn"))
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._toggle_btn)
        btn_row.addWidget(self._remove_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self._repair_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._refresh()

    def _has_dlclist(self) -> bool:
        return bool(self._dlclist_xml) and Path(self._dlclist_xml).is_file()

    def _read_dlclist(self) -> str:
        if not self._has_dlclist():
            return ""
        try:
            return Path(self._dlclist_xml).read_text(encoding="utf-8")
        except OSError:
            return ""

    def _sort_mode(self) -> str:
        return self._sort_combo.currentData()

    def _on_sort_changed(self, *_) -> None:
        # the chosen sort is remembered across sessions automatically
        self._config.manage_sort = self._sort_mode()
        self._config.save()
        self._refresh()

    def _refresh(self, *_) -> None:
        keep = self._selected_name()  # restore the selection after the rebuild
        # guard so rebuilding the list does not trigger the row moved handler
        self._loading = True
        try:
            self._populate(keep)
        finally:
            self._loading = False
        self._sync_buttons()

    def _populate(self, keep: str | None) -> None:
        self._list.clear()

        text = self._read_dlclist()
        disabled = set(dlclist.list_disabled_entries(text))
        active = set(dlclist.list_active_entries(text))
        dupes = set(dlclist.find_duplicate_entries(text))
        order = {name: i for i, name in enumerate(dlclist.list_ordered_entries(text))}

        if dupes and not self._warned_dupes:
            for name in sorted(dupes):
                self._log_line("XML", "err", T("dlclist_duplicate", name=name))
            self._warned_dupes = True

        infos = list_installed_dlc_info(self._dlcpacks_dir)
        query = self._search.text().strip().lower()
        if query:
            infos = [d for d in infos if query in d.name.lower()]

        mode = self._sort_mode()
        if mode == "date":
            infos.sort(key=lambda d: d.added, reverse=True)
        elif mode == "order":
            infos.sort(key=lambda d: (order.get(d.name, len(order)), d.name.lower()))
        else:
            infos.sort(key=lambda d: d.name.lower())

        if not infos:
            empty_key = "manage_no_matches" if query else "manage_empty"
            placeholder = QListWidgetItem(T(empty_key))
            placeholder.setFlags(Qt.NoItemFlags)
            self._list.addItem(placeholder)
            return

        for d in infos:
            if d.name in disabled:
                state = self._DISABLED
            elif d.name in active:
                state = self._ACTIVE
            else:
                state = self._UNLISTED
            dot, pill_fg, pill_bg = self._STATE_STYLE[state]
            pills = []
            if self._has_dlclist():
                pills.append((T(f"manage_state_{state}"), pill_fg, pill_bg))
            if d.name in dupes:
                pills.append((T("manage_state_duplicate"), *self._DUPLICATE_PILL))

            when = datetime.fromtimestamp(d.added).strftime("%Y-%m-%d %H:%M")
            meta = T("manage_added", date=when)
            row = _ModRow(d.name, meta, dot, pills)

            item = QListWidgetItem()
            item.setData(Qt.UserRole, d.name)
            item.setData(Qt.UserRole + 1, state)
            item.setSizeHint(row.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, row)
            if d.name == keep:
                self._list.setCurrentItem(item)

    def _sync_buttons(self) -> None:
        name = self._selected_name()
        state = self._selected_state()
        self._remove_btn.setEnabled(name is not None)
        self._repair_btn.setEnabled(self._has_dlclist())
        self._toggle_btn.setEnabled(name is not None and self._has_dlclist())
        if state == self._ACTIVE:
            self._toggle_btn.setText(T("manage_disable_btn"))
        else:
            self._toggle_btn.setText(T("manage_enable_btn"))
        can_reorder = (
            self._has_dlclist()
            and self._sort_mode() == "order"
            and not self._search.text().strip()
        )
        self._list.setDragDropMode(
            QAbstractItemView.InternalMove
            if can_reorder
            else QAbstractItemView.NoDragDrop
        )

    def _selected_state(self) -> str | None:
        item = self._list.currentItem()
        if item is None or not (item.flags() & Qt.ItemIsSelectable):
            return None
        return item.data(Qt.UserRole + 1)

    def _selected_name(self) -> str | None:
        item = self._list.currentItem()
        if item is None or not (item.flags() & Qt.ItemIsSelectable):
            return None
        return item.data(Qt.UserRole)

    def _on_rows_moved(self, *_) -> None:
        if self._loading or not self._has_dlclist():
            return
        listed = set(dlclist.list_ordered_entries(self._read_dlclist()))
        order = []
        for i in range(self._list.count()):
            name = self._list.item(i).data(Qt.UserRole)
            if name in listed:
                order.append(name)
        try:
            dlclist.set_order_in_file(Path(self._dlclist_xml), order)
        except Exception as exc:
            self._log_line("XML", "err", T("dlclist_error", err=str(exc)))
        # the internal drag move drops the row widgets so rebuild the list
        self._refresh()

    def _toggle_selected(self) -> None:
        name = self._selected_name()
        if name is None or not self._has_dlclist():
            return
        path = Path(self._dlclist_xml)
        try:
            if self._selected_state() == self._ACTIVE:
                if dlclist.disable_in_file(path, name):
                    self._log_line("XML", "ok", T("dlclist_disabled", name=name))
            else:
                changed = dlclist.enable_in_file(path, name)
                if not changed:
                    changed = dlclist.update_file(path, name)
                if changed:
                    self._log_line("XML", "ok", T("dlclist_enabled", name=name))
        except Exception as exc:
            self._log_line("XML", "err", T("dlclist_error", err=str(exc)))
        self._refresh()

    def _repair(self) -> None:
        if not self._has_dlclist():
            return
        path = Path(self._dlclist_xml)
        text = self._read_dlclist()
        registered = set(dlclist.list_entries(text))
        installed = {d.name for d in list_installed_dlc_info(self._dlcpacks_dir)}
        orphans = sorted(installed - registered)
        missing = sorted(registered - installed)

        if not orphans and not missing:
            self._log_line("XML", "info", T("repair_none"))
            return

        added = 0
        for name in orphans:
            try:
                if dlclist.update_file(path, name):
                    self._log_line("XML", "ok", T("repair_added", name=name))
                    added += 1
            except Exception as exc:
                self._log_line("XML", "err", T("dlclist_error", err=str(exc)))

        removed = kept = 0
        decide = _ReplaceDecider(
            self, "repair_missing_body",
            offer_all=len(missing) > 1, title_key="repair_missing_title",
        )
        for name in missing:
            if not decide(name):
                kept += 1
                continue
            try:
                if dlclist.remove_from_file(path, name):
                    self._log_line("XML", "ok", T("repair_removed", name=name))
                    removed += 1
            except Exception as exc:
                self._log_line("XML", "err", T("dlclist_error", err=str(exc)))

        self._log_line(
            "XML", "info", T("repair_summary", added=added, removed=removed, kept=kept)
        )
        self._refresh()

    def _remove_selected(self) -> None:
        name = self._selected_name()
        if name is None:
            return
        reply = QMessageBox.question(
            self,
            T("manage_confirm_title"),
            T("manage_confirm_body", name=name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        dlc_log = lambda msg: self._log_line("DLC", "work", msg)
        result = uninstall_dlc(name, self._dlcpacks_dir, dlc_log)
        self._log_line("DLC", "ok" if result.ok else "err", result.message)
        if result.ok and self._dlclist_xml and Path(self._dlclist_xml).is_file():
            try:
                if dlclist.remove_from_file(Path(self._dlclist_xml), name):
                    self._log_line("XML", "ok", T("dlclist_entry_removed", name=name))
            except Exception as exc:
                self._log_line("XML", "err", T("dlclist_error", err=str(exc)))
        self._refresh()


class ElsFolderDialog(QDialog):

    def __init__(self, root: Path, groups, default: Path, parent=None) -> None:
        super().__init__(parent)
        self._chosen: Path | None = None
        self.setWindowTitle(T("els_pick_title"))
        self.setModal(True)
        self.resize(500, 340)

        layout = QVBoxLayout(self)
        hint = QLabel(T("els_pick_hint"))
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "background-color:#1c1c1e; color:#ddd; border:1px solid #444; border-radius:6px;"
        )
        self._list.itemDoubleClicked.connect(lambda *_: self._accept())
        layout.addWidget(self._list, 1)

        for folder in sorted(groups, key=lambda f: str(f).lower()):
            try:
                rel = folder.relative_to(root)
                label = T("els_pick_root") if str(rel) == "." else str(rel)
            except ValueError:
                label = folder.name
            text = f"{label}    ·    {T('els_pick_count', n=len(groups[folder]))}"
            if folder == default:
                text += "    " + T("els_pick_recommended")
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, str(folder))
            self._list.addItem(item)
            if folder == default:
                self._list.setCurrentItem(item)
        if self._list.currentItem() is None and self._list.count():
            self._list.setCurrentRow(0)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        self._chosen = Path(item.data(Qt.UserRole))
        self.accept()

    def chosen(self) -> Path | None:
        return self._chosen


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

        logo_path = _asset_path("logo.png")
        if os.path.exists(logo_path):
            logo_lbl = QLabel()
            pixmap = QPixmap(logo_path)
            logo_lbl.setPixmap(
                pixmap.scaledToHeight(96, Qt.SmoothTransformation)
            )
            logo_lbl.setAlignment(Qt.AlignCenter)
            root_layout.addWidget(logo_lbl)

        path_row = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setStyleSheet("color: #ddd;")
        self.choose_btn = QPushButton()
        self.choose_btn.clicked.connect(self.choose_gta_path)
        self.settings_btn = QPushButton()
        self.settings_btn.clicked.connect(self.open_settings)
        self.manage_btn = QPushButton()
        self.manage_btn.clicked.connect(self.manage_mods)
        path_row.addWidget(self.path_label, stretch=1)
        path_row.addWidget(self.choose_btn)
        path_row.addWidget(self.manage_btn)
        path_row.addWidget(self.settings_btn)
        root_layout.addLayout(path_row)

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

        self.zone = DropZone(T("drop_zone_title"), T("drop_zone_hint"), self.on_drop)
        root_layout.addWidget(self.zone)

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

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "background-color: #181818; color: #ddd; "
            "font-family: Consolas, 'Courier New', monospace; font-size: 12px;"
        )
        root_layout.addWidget(self.log, stretch=1)
        self._progress_on = False
        self._busy = False
        self._history: list[tuple[str, str, str]] = []

        self._apply_dark_palette()
        self.retranslate_ui()
        self._restore_history()
        self._first_run_autodetect()

    def _init_language(self) -> None:
        saved = self.config.language
        if saved and saved in LANGUAGES:
            i18n.set_language(saved)
            return
        i18n.set_language(_system_default_language())
        dlg = LanguageDialog(i18n.get_language(), parent=self)
        dlg.exec()
        i18n.set_language(dlg.chosen())
        self.config.language = i18n.get_language()
        self.config.save()

    def open_settings(self) -> None:
        dlg = SettingsDialog(
            i18n.get_language(), self.config.save_terminal_history, parent=self
        )
        if dlg.exec() != QDialog.Accepted:
            return
        self.config.save_terminal_history = dlg.save_history()
        if not self.config.save_terminal_history:
            self.config.terminal_history = []  # forget what was kept once turned off
        new_lang = dlg.language()
        if new_lang and new_lang != i18n.get_language():
            i18n.set_language(new_lang)
            self.config.language = new_lang
            self.retranslate_ui()
        self.config.save()

    def manage_mods(self) -> None:
        paths = self._ensure_paths()
        if not paths:
            return
        dlg = ManageModsDialog(
            paths["dlcpacks"], self.config.dlclist_xml_path, self.log_line,
            self.config, parent=self,
        )
        dlg.exec()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(T("window_title"))
        self.choose_btn.setText(T("choose_gta_btn"))
        self.manage_btn.setText(T("manage_btn"))
        self.settings_btn.setText(T("settings_btn"))
        self.mods_checkbox.setText(T("mods_checkbox"))
        self.zone.set_texts(T("drop_zone_title"), T("drop_zone_hint"))
        self.xml_btn.setText(T("dlclist_btn"))
        self.clear_xml_btn.setText(T("dlclist_clear_btn"))
        self._refresh_labels()

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
            self.log_line("INFO", "ok", T("gta_detected", path=str(default)))
        else:
            self.log_line("INFO", "info", T("gta_not_detected"))

    def log_line(self, group: str, status: str, text: str) -> None:
        self._history.append((group, status, text))
        self._render_log(group, status, text)

    def _render_log(self, group: str, status: str, text: str) -> None:
        self._clear_progress()
        glyph, scolor = _STATUS.get(status, _STATUS["info"])
        gcolor = _GROUP_COLORS.get(group, _GROUP_COLORS["INFO"])
        parts = [f'<span style="color:{gcolor}">[{group}]</span>']
        if glyph:
            parts.append(f'<span style="color:{scolor}">{glyph}</span>')
        parts.append(
            f'<span style="color:{_TEXT_COLOR}">{html.escape(text)}</span>'
        )
        self._append_html(" ".join(parts))

    def _restore_history(self) -> None:
        if not self.config.save_terminal_history:
            return
        # render saved lines without re-recording them into _history
        entries = [tuple(e) for e in self.config.terminal_history if len(e) == 3]
        self._history = list(entries)
        for group, status, text in entries:
            self._render_log(group, status, text)
        if entries:
            self._render_log("INFO", "info", T("history_restored"))

    def closeEvent(self, event) -> None:
        if self.config.save_terminal_history:
            self.config.terminal_history = self._history[-1000:]  # cap growth
        else:
            self.config.terminal_history = []
        self.config.save()
        super().closeEvent(event)

    def log_msg(self, msg: str) -> None:
        self.log_line("INFO", "info", msg)

    def _group_logger(self, group: str):
        return lambda msg: self.log_line(group, "work", msg)

    def _append_html(self, line_html: str) -> None:
        cur = self.log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        if not self.log.document().isEmpty():
            cur.insertBlock()
        cur.insertHtml(line_html)
        self.log.setTextCursor(cur)
        self.log.ensureCursorVisible()

    def _show_progress(self, group: str, done: int, total: int, label: str) -> None:
        frac = 1.0 if total <= 0 else max(0.0, min(1.0, done / total))
        filled = round(frac * _PROGRESS_WIDTH)
        bar = "█" * filled + "░" * (_PROGRESS_WIDTH - filled)
        gcolor = _GROUP_COLORS.get(group, _GROUP_COLORS["INFO"])
        text = f"[{bar}] {int(frac * 100):3d}%"
        if label:
            text += f"  {label}"
        line_html = (
            f'<span style="color:{gcolor}">[{group}]</span> '
            f'<span style="color:{_TEXT_COLOR}">{html.escape(text)}</span>'
        )
        cur = self.log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        if self._progress_on:
            # overwrite the existing bar line in place instead of stacking lines
            cur.movePosition(
                QTextCursor.MoveOperation.StartOfBlock,
                QTextCursor.MoveMode.KeepAnchor,
            )
            cur.removeSelectedText()
        else:
            if not self.log.document().isEmpty():
                cur.insertBlock()
            self._progress_on = True
        cur.insertHtml(line_html)
        self.log.setTextCursor(cur)
        self.log.ensureCursorVisible()
        QApplication.processEvents()  # keep the bar animating during long copies

    def _clear_progress(self) -> None:
        if not self._progress_on:
            return
        cur = self.log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        cur.movePosition(
            QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor
        )
        cur.removeSelectedText()
        cur.deletePreviousChar()
        self._progress_on = False

    def _ensure_paths(self):
        gta = self.config.gta_path
        if not gta or not is_gta_root(Path(gta)):
            QMessageBox.warning(self, T("gta_missing_title"), T("gta_missing_body"))
            return None
        return derive_paths(Path(gta), use_mods=self.config.use_mods_folder)

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
        self.log_line("INFO", "ok", T("gta_path_set", path=str(path)))

    def choose_dlclist_xml(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, T("choose_dlclist_dialog"), "", "XML (*.xml)"
        )
        if not path:
            return
        self.config.dlclist_xml_path = path
        self.config.save()
        self._refresh_labels()
        self.log_line("XML", "ok", T("dlclist_set", path=path))

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
            self.log_line("INFO", "info", T("direct_enabled"))
        else:
            self.log_line("INFO", "info", T("safe_enabled"))
        self.config.use_mods_folder = checked
        self.config.save()
        self._refresh_labels()

    def on_drop(self, srcs: list[Path]) -> None:
        if self._busy:
            return
        if not srcs:
            self.log_line("INFO", "err", T("drop_nothing"))
            return
        paths = self._ensure_paths()
        if not paths:
            return

        self._set_busy(True)
        temp_dirs: list[Path] = []
        try:
            scan_items = self._expand_sources(srcs, temp_dirs)

            dlc_packs: list[Path] = []
            els_jobs: list[tuple[Path, list[Path]]] = []
            unknown: list[str] = []
            for path, display, deep in scan_items:
                if deep:
                    packs = find_dlc_packs_deep(path)
                    has_els = bool(list_els_xmls(path))
                    if packs:
                        dlc_packs.extend(packs)
                    if has_els:
                        els_jobs.append((path, packs))
                    if not packs and not has_els:
                        unknown.append(display)
                else:
                    packs = find_dlc_packs(path)
                    if packs:
                        dlc_packs.extend(packs)
                    elif is_els_source(path):
                        els_jobs.append((path, []))
                    else:
                        unknown.append(display)

            els_srcs: list[Path] = []
            for path, packs in els_jobs:
                chosen = self._resolve_els_source(path, packs)
                if chosen is not None:
                    els_srcs.append(chosen)

            els_count = sum(len(list_els_xmls(s)) for s in els_srcs)
            dlc_decide = _ReplaceDecider(
                self, "dlc_replace_body", offer_all=len(dlc_packs) > 1
            )
            els_decide = _ReplaceDecider(
                self, "els_replace_body", offer_all=els_count > 1
            )

            for pack in dlc_packs:
                try:
                    self._install_dlc_pack(pack, paths, dlc_decide)
                except Exception as exc:
                    self.log_line("DLC", "err", T("unexpected_error", err=str(exc)))
            for src in els_srcs:
                try:
                    self._install_els_src(src, paths, els_decide)
                except Exception as exc:
                    self.log_line("ELS", "err", T("unexpected_error", err=str(exc)))
            for name in unknown:
                self.log_line("INFO", "err", T("drop_unknown", name=name))
        finally:
            self._set_busy(False)
            for d in temp_dirs:
                shutil.rmtree(d, ignore_errors=True)

    def _expand_sources(
        self, srcs: list[Path], temp_dirs: list[Path]
    ) -> list[tuple[Path, str, bool]]:
        items: list[tuple[Path, str, bool]] = []
        for src in srcs:
            if not archive.is_archive(src):
                items.append((src, src.name, False))
                continue
            self.log_line("INFO", "work", T("archive_extracting", name=src.name))
            try:
                dest = archive.extract_to_temp(src)
            except archive.CorruptArchive:
                self.log_line("INFO", "err", T("archive_corrupt", name=src.name))
                continue
            except archive.UnsupportedArchive as exc:
                self.log_line(
                    "INFO", "err", T("archive_unsupported", name=src.name, fmt=str(exc))
                )
                continue
            except archive.ArchiveError as exc:
                self.log_line(
                    "INFO", "err", T("archive_failed", name=src.name, err=str(exc))
                )
                continue
            temp_dirs.append(dest.parent)
            self.log_line("INFO", "ok", T("archive_extracted", name=src.name))
            items.append((dest, src.name, True))
        return items

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.zone.setAcceptDrops(not busy)
        for w in (
            self.zone,
            self.choose_btn,
            self.manage_btn,
            self.settings_btn,
            self.mods_checkbox,
            self.xml_btn,
            self.clear_xml_btn,
        ):
            w.setEnabled(not busy)

    def _install_dlc_pack(self, pack, paths, decide) -> None:
        log = self._group_logger("DLC")
        progress = lambda done, total, name: self._show_progress(
            "DLC", done, total, name
        )
        result = install_dlc(pack, paths["dlcpacks"], log, progress=progress)
        if result.conflict:
            if not decide(pack.name):
                self.log_line("DLC", "info", T("dlc_kept", name=pack.name))
                return
            result = install_dlc(
                pack, paths["dlcpacks"], log, overwrite=True, progress=progress
            )
        self.log_line("DLC", "ok" if result.ok else "err", result.message)
        if result.ok and result.dlc_name:
            self._handle_dlclist_update(result.dlc_name)

    def _resolve_els_source(self, src, pack_folders):
        groups = group_els_by_folder(src)
        if len(groups) <= 1 or not els_has_name_collision(groups):
            return src
        if not pack_folders:
            pack_folders = find_dlc_packs_deep(src)
        default = closest_els_folder(sorted(groups), pack_folders)
        dlg = ElsFolderDialog(src, groups, default, parent=self)
        if dlg.exec() != QDialog.Accepted or dlg.chosen() is None:
            self.log_line("ELS", "info", T("els_variant_skipped"))
            return None
        chosen = dlg.chosen()
        self.log_line("ELS", "info", T("els_variant_chosen", folder=chosen.name))
        return chosen

    def _install_els_src(self, src, paths, decide) -> None:
        log = self._group_logger("ELS")
        progress = lambda done, total, name: self._show_progress(
            "ELS", done, total, name
        )
        target = paths["root"] / "ELS" / "pack_default"
        result = install_els(src, target, log, resolve=decide, progress=progress)
        self.log_line("ELS", "ok" if result.ok else "err", result.message)

    def _handle_dlclist_update(self, dlc_name: str) -> None:
        xml = self.config.dlclist_xml_path
        if xml and Path(xml).is_file():
            try:
                changed = dlclist.update_file(Path(xml), dlc_name)
            except Exception as exc:
                self.log_line("XML", "err", T("dlclist_error", err=str(exc)))
                return
            if changed:
                self.log_line("XML", "ok", T("dlclist_added", name=dlc_name))
            else:
                self.log_line("XML", "info", T("dlclist_existed", name=dlc_name))
            return
        entry = f"    <Item>dlcpacks:/{dlc_name}/</Item>"
        self.log_line("XML", "info", T("dlclist_hint_no_xml", entry=entry))


def _set_windows_app_id() -> None:
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
