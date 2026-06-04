"""Main GUI window built with PySide6."""
from __future__ import annotations

import html
import os
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

import dlclist
import i18n
from config import Config
from gta_detect import derive_paths, find_default_install, is_gta_root
from i18n import LANGUAGES, T
from installers import (
    find_dlc_packs,
    install_dlc,
    install_els,
    is_els_source,
    list_els_xmls,
    list_installed_dlc_info,
    uninstall_dlc,
)


# Log line styling. Each message starts with a coloured group tag ([DLC],
# [ELS], [XML] = dlclist.xml, [INFO]) and a status glyph.
_GROUP_COLORS = {
    "DLC": "#4aa3ff",   # blue
    "ELS": "#46c46a",   # green
    "XML": "#e0a030",   # orange
    "INFO": "#9aa0a6",  # grey
}
_STATUS = {
    "ok":   ("✓", "#46c46a"),  # check, green
    "err":  ("✗", "#e05545"),  # cross, red
    "work": ("→", "#9aa0a6"),  # arrow, grey
    "info": ("",       "#9aa0a6"),  # no glyph
}
_TEXT_COLOR = "#dddddd"
_PROGRESS_WIDTH = 24  # characters in the ASCII progress bar


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


class _ReplaceDecider:
    """Per-item replace prompt that remembers a 'to all' choice.

    Used while installing a batch (several DLC packs or ELS files): the first
    conflict offers Yes / No / Yes to All / No to All. Picking a "to all"
    button answers every remaining conflict in the batch without re-asking.
    The "to all" buttons are only shown when `offer_all` is set (i.e. more
    than one file is being installed) — for a single file they'd be pointless.
    """

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
        self._all: bool | None = None  # None = keep asking

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
    """A labelled drop target that calls back with all dropped paths at once.

    Passing the whole batch (rather than one path per call) lets the handler
    apply a single "replace all / keep all" decision across everything dropped.
    """

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
    """A modern, at-a-glance row for one installed DLC pack.

    Shows a coloured status dot, the pack name, a meta line (date added) and one
    or more state pills (e.g. "active", "disabled", "duplicate"). The widget is
    translucent so the list's own selection highlight shows through behind it.
    """

    def __init__(self, name: str, meta: str, dot_color: str, pills) -> None:
        super().__init__()
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
    """List installed DLC packs and let the user manage them.

    Per pack the user can enable/disable it, remove it, and (in load-order mode)
    move it up or down. Disabling comments the entry out in dlclist.xml: the
    folder stays on disk and the pack simply isn't loaded, so it reads as
    "switched off", not "missing". A repair action reconciles dlclist.xml with
    the folders actually present, and duplicate entries are flagged on sight.
    """

    # Per-item state, used to label the toggle button and colour the row.
    _ACTIVE = "active"        # folder present, listed and loaded
    _DISABLED = "disabled"    # folder present, listed but commented out
    _UNLISTED = "unlisted"    # folder present but no dlclist.xml entry

    # state -> (dot colour, pill text colour, pill background)
    _STATE_STYLE = {
        _ACTIVE:   ("#46c46a", "#7fe39a", "rgba(70,196,106,0.18)"),
        _DISABLED: ("#8a8f94", "#b8bdc2", "rgba(138,143,148,0.18)"),
        _UNLISTED: ("#e0a030", "#f0c060", "rgba(224,160,48,0.18)"),
    }
    _DUPLICATE_PILL = ("#ff8a7a", "rgba(224,85,69,0.22)")

    def __init__(self, dlcpacks_dir: Path, dlclist_xml: str, log_line, parent=None):
        super().__init__(parent)
        self._dlcpacks_dir = dlcpacks_dir
        self._dlclist_xml = dlclist_xml
        self._log_line = log_line  # (group, status, text) -> None
        self._warned_dupes = False  # log the duplicate warning only once

        self.setWindowTitle(T("manage_dialog_title"))
        self.setModal(True)
        self.resize(540, 440)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # --- search + sort controls ---
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
        self._sort_combo.currentIndexChanged.connect(self._refresh)
        top_row.addWidget(self._search, 1)
        top_row.addWidget(self._sort_label)
        top_row.addWidget(self._sort_combo)
        layout.addLayout(top_row)

        # --- list (drag to reorder in load-order mode) ---
        self._loading = False  # guards rowsMoved while _refresh rebuilds the list
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

        # --- action buttons ---
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
        """dlclist.xml text, or '' if none is configured / it can't be read."""
        if not self._has_dlclist():
            return ""
        try:
            return Path(self._dlclist_xml).read_text(encoding="utf-8")
        except OSError:
            return ""

    def _sort_mode(self) -> str:
        return self._sort_combo.currentData()

    def _refresh(self, *_) -> None:  # *_ swallows signal args (combo index / text)
        keep = self._selected_name()  # restore selection across the rebuild
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
            infos.sort(key=lambda d: d.added, reverse=True)  # newest first
        elif mode == "order":
            # Load order from dlclist.xml; packs with no entry sink to the bottom.
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
        # Disabling/enabling only makes sense when a dlclist.xml is configured.
        self._toggle_btn.setEnabled(name is not None and self._has_dlclist())
        if state == self._ACTIVE:
            self._toggle_btn.setText(T("manage_disable_btn"))
        else:
            self._toggle_btn.setText(T("manage_enable_btn"))
        # Drag-to-reorder is only meaningful when the list shows the real load
        # order in full (load-order mode, no search filtering the view).
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
        """Persist a drag-reorder: write the list's new order into dlclist.xml."""
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
        self._refresh()  # rebuild the row widgets the internal move discarded

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
                # Re-enable: uncomment if disabled, otherwise add a fresh entry.
                changed = dlclist.enable_in_file(path, name)
                if not changed:
                    changed = dlclist.update_file(path, name)
                if changed:
                    self._log_line("XML", "ok", T("dlclist_enabled", name=name))
        except Exception as exc:
            self._log_line("XML", "err", T("dlclist_error", err=str(exc)))
        self._refresh()

    def _repair(self) -> None:
        """Reconcile dlclist.xml with the folders actually present.

        Folders without an entry are re-added automatically; entries whose
        folder is gone are removed only after the user confirms (per item, with
        a "to all" shortcut).
        """
        if not self._has_dlclist():
            return
        path = Path(self._dlclist_xml)
        text = self._read_dlclist()
        registered = set(dlclist.list_entries(text))
        installed = {d.name for d in list_installed_dlc_info(self._dlcpacks_dir)}
        orphans = sorted(installed - registered)   # folder present, no entry
        missing = sorted(registered - installed)   # entry present, folder gone

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
        self.manage_btn = QPushButton()
        self.manage_btn.clicked.connect(self.manage_mods)
        path_row.addWidget(self.path_label, stretch=1)
        path_row.addWidget(self.choose_btn)
        path_row.addWidget(self.manage_btn)
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

        # --- Drop zone --------------------------------------------------
        # One box for everything: the app detects DLC vs ELS per dropped item.
        self.zone = DropZone(T("drop_zone_title"), T("drop_zone_hint"), self.on_drop)
        root_layout.addWidget(self.zone)

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
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "background-color: #181818; color: #ddd; "
            "font-family: Consolas, 'Courier New', monospace; font-size: 12px;"
        )
        root_layout.addWidget(self.log, stretch=1)
        self._progress_on = False  # is the last log line a live progress bar?
        self._busy = False  # an install is running (drops are blocked)

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

    def manage_mods(self) -> None:
        paths = self._ensure_paths()
        if not paths:
            return
        dlg = ManageModsDialog(
            paths["dlcpacks"], self.config.dlclist_xml_path, self.log_line, parent=self
        )
        dlg.exec()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(T("window_title"))
        self.choose_btn.setText(T("choose_gta_btn"))
        self.manage_btn.setText(T("manage_btn"))
        self.lang_btn.setText(T("lang_button"))
        self.mods_checkbox.setText(T("mods_checkbox"))
        self.zone.set_texts(T("drop_zone_title"), T("drop_zone_hint"))
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
            self.log_line("INFO", "ok", T("gta_detected", path=str(default)))
        else:
            self.log_line("INFO", "info", T("gta_not_detected"))

    # ----- logging ----- #
    def log_line(self, group: str, status: str, text: str) -> None:
        """Append a coloured `[GROUP] <glyph> text` line to the log."""
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

    def log_msg(self, msg: str) -> None:
        """Backwards-compatible plain logger (treated as an INFO line)."""
        self.log_line("INFO", "info", msg)

    def _group_logger(self, group: str):
        """A single-arg `LogFn` that logs into `group` as a progress/work line.

        Used for the installers' internal `log(text)` calls, which don't know
        about groups or status.
        """
        return lambda msg: self.log_line(group, "work", msg)

    def _append_html(self, line_html: str) -> None:
        cur = self.log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        if not self.log.document().isEmpty():
            cur.insertBlock()
        cur.insertHtml(line_html)
        self.log.setTextCursor(cur)
        self.log.ensureCursorVisible()

    # ----- progress bar (lives as the last log line) ----- #
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
            # Replace the existing bar line in place.
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
        QApplication.processEvents()

    def _clear_progress(self) -> None:
        if not self._progress_on:
            return
        cur = self.log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        cur.movePosition(
            QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor
        )
        cur.removeSelectedText()
        cur.deletePreviousChar()  # drop the now-empty line's separator
        self._progress_on = False

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

    # ----- drop callback ----- #
    def on_drop(self, srcs: list[Path]) -> None:
        if self._busy:  # an install is already running (event loop is pumped)
            return
        if not srcs:
            self.log_line("INFO", "err", T("drop_nothing"))
            return
        paths = self._ensure_paths()
        if not paths:
            return

        # Classify everything first: detect DLC packs vs ELS files per dropped
        # item so we know how many files of each kind there are. The "replace
        # all / keep all" buttons are only offered when a kind has >1 file.
        dlc_packs: list[Path] = []
        els_srcs: list[Path] = []
        unknown: list[Path] = []
        for src in srcs:
            packs = find_dlc_packs(src)
            if packs:
                dlc_packs.extend(packs)
            elif is_els_source(src):
                els_srcs.append(src)
            else:
                unknown.append(src)

        els_count = sum(len(list_els_xmls(s)) for s in els_srcs)
        # One decider per kind so a "to all" choice carries across the drop.
        dlc_decide = _ReplaceDecider(
            self, "dlc_replace_body", offer_all=len(dlc_packs) > 1
        )
        els_decide = _ReplaceDecider(
            self, "els_replace_body", offer_all=els_count > 1
        )

        self._set_busy(True)
        try:
            for pack in dlc_packs:
                try:
                    self._install_dlc_pack(pack, paths, dlc_decide)
                except Exception as exc:  # never swallow a failure silently
                    self.log_line("DLC", "err", T("unexpected_error", err=str(exc)))
            for src in els_srcs:
                try:
                    self._install_els_src(src, paths, els_decide)
                except Exception as exc:
                    self.log_line("ELS", "err", T("unexpected_error", err=str(exc)))
            for src in unknown:
                self.log_line("INFO", "err", T("drop_unknown", name=src.name))
        finally:
            self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        """Block further input while a copy runs (the event loop is pumped)."""
        self._busy = busy
        self.zone.setAcceptDrops(not busy)
        for w in (
            self.zone,
            self.choose_btn,
            self.manage_btn,
            self.lang_btn,
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

    def _install_els_src(self, src, paths, decide) -> None:
        log = self._group_logger("ELS")
        progress = lambda done, total, name: self._show_progress(
            "ELS", done, total, name
        )
        target = paths["root"] / "ELS" / "pack_default"
        result = install_els(src, target, log, resolve=decide, progress=progress)
        self.log_line("ELS", "ok" if result.ok else "err", result.message)

    # ----- dlclist.xml handling ----- #
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
