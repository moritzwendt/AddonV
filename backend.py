from __future__ import annotations

import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    QObject, Property, Signal, Slot, QUrl, QCoreApplication, QEventLoop,
)
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import QColorDialog, QFileDialog

import archive
import dlclist
import i18n
import profiles
import renamer
import theme
import updater
from config import Config
from dialogs import ReplaceDecider
from gta_detect import derive_paths, find_default_install, is_gta_root
from i18n import LANGUAGES, T
from installers import (
    closest_els_folder,
    derive_group_name,
    els_has_name_collision,
    find_dlc_packs,
    find_dlc_packs_deep,
    group_els_by_folder,
    group_els_by_install_time,
    install_dlc,
    install_els,
    install_path,
    is_els_source,
    list_els_xmls,
    list_installed_dlc_info,
    list_installed_els,
    uninstall_dlc,
)


class Backend(QObject):

    logAppended = Signal(str, str, str)
    progress = Signal(float, str)        
    textsChanged = Signal()
    settingsChanged = Signal()
    accentChanged = Signal()
    sidebarChanged = Signal()
    modsListChanged = Signal()
    busyChanged = Signal()
    summaryChanged = Signal()
    uiRevisionChanged = Signal()
    profilesChanged = Signal()
    zonesChanged = Signal()
    renameChanged = Signal()
    renamePresetsChanged = Signal()
    dialogRequested = Signal("QVariant")

    def __init__(self) -> None:
        super().__init__()
        self.config = Config.load()
        self._busy = False
        self._ui_revision = 0
        self._history: list[tuple[str, str, str]] = []
        self._packs: list = []
        self._installed = None
        self._els_sets = 0
        self._els_view: list = []
        self._install_state = "ready"
        self._last_summary = ""
        self._warned_dupes: set[str] = set()
        self._update_thread = None
        self._rename_files: list[Path] = []
        self._rename_base = ""
        self._rename_state = "ready"
        self._rename_summary = ""
        self._rename_els_like: dict[str, bool] = {}
        self._dialog_loops: list[QEventLoop] = []
        self._dialog_result = ""
        self._needs_language = False
        self._init_language()
        self._restore_history()

    def _init_language(self) -> None:
        saved = self.config.language
        if saved and saved in LANGUAGES:
            i18n.set_language(saved)
            return
        name = ""
        try:
            from PySide6.QtCore import QLocale
            name = QLocale.system().name().lower().split("_", 1)[0]
        except Exception:
            pass
        i18n.set_language(name if name in LANGUAGES else "en")
        self._needs_language = True

    def _language_options(self) -> list:
        return [{"value": code, "label": label} for code, label in LANGUAGES.items()]

    @Slot()
    def promptInitialLanguage(self) -> None:
        if not self._needs_language:
            return
        self._needs_language = False
        chosen = self._pick(
            T("lang_dialog_title"), T("lang_dialog_hint"),
            self._language_options(), i18n.get_language(),
        )
        code = chosen if chosen in LANGUAGES else i18n.get_language()
        i18n.set_language(code)
        self.config.language = code
        self.config.save()
        self._ui_revision += 1
        self.uiRevisionChanged.emit()
        self.textsChanged.emit()
        self.settingsChanged.emit()
        self.reloadMods()

    def _restore_history(self) -> None:
        if not self.config.save_terminal_history:
            return
        self._history = [
            tuple(e) for e in self.config.terminal_history if len(e) == 3
        ]
        if self._history:
            self._history.append(("INFO", "info", T("history_restored")))

    @Slot()
    def saveOnClose(self) -> None:
        if self.config.save_terminal_history:
            self.config.terminal_history = self._history[-1000:]
        else:
            self.config.terminal_history = []
        self.config.save()

    def _log(self, group: str, status: str, text: str) -> None:
        self._history.append((group, status, text))
        self.logAppended.emit(group, status, text)

    def _group_logger(self, group: str):
        return lambda msg: self._log(group, "work", msg)

    def _show_progress(self, group, done, total, label) -> None:
        frac = 1.0 if total <= 0 else max(0.0, min(1.0, done / total))
        self.progress.emit(frac, label or "")
        QCoreApplication.processEvents()

    def _ask(self, spec: dict) -> str:
        loop = QEventLoop()
        self._dialog_loops.append(loop)
        self._dialog_result = ""
        self.dialogRequested.emit(spec)
        loop.exec()
        return self._dialog_result

    @Slot(str)
    def resolveDialog(self, choice: str) -> None:
        self._dialog_result = choice or ""
        if self._dialog_loops:
            self._dialog_loops.pop().quit()

    def _info(self, title: str, body: str) -> None:
        self._ask({
            "template": "message", "title": title, "body": body,
            "cancelId": "ok",
            "buttons": [{"id": "ok", "label": T("ok"), "kind": "solid"}],
        })

    def _confirm(self, title: str, body: str,
                 confirm_label: str = "", danger: bool = False) -> bool:
        return self._ask({
            "template": "message", "title": title, "body": body,
            "cancelId": "no",
            "buttons": [
                {"id": "no", "label": T("cancel"), "kind": "ghost"},
                {"id": "yes", "label": confirm_label or T("yes"),
                 "kind": "danger" if danger else "solid"},
            ],
        }) == "yes"

    def _choose(self, title: str, body: str, buttons: list, cancel_id: str = "") -> str:
        return self._ask({
            "template": "message", "title": title, "body": body,
            "cancelId": cancel_id, "buttons": buttons,
        })

    def _pick(self, title: str, body: str, options: list, selected: str = "") -> str:
        return self._ask({
            "template": "picker", "title": title, "body": body,
            "options": options, "selected": selected, "cancelId": "",
        })

    @Slot(str, result=str)
    def tr(self, key: str) -> str:
        return T(key)

    def _get_history(self):
        return [{"group": g, "status": s, "text": t} for g, s, t in self._history]
    history = Property("QVariantList", _get_history, constant=True)

    def _get_languages(self):
        return [{"code": c, "label": n} for c, n in LANGUAGES.items()]
    languages = Property("QVariantList", _get_languages, constant=True)

    def _get_version(self):
        return updater.CURRENT_VERSION
    version = Property(str, _get_version, constant=True)

    def _get_accent(self):
        return self.config.accent
    accent = Property(str, _get_accent, notify=accentChanged)

    def _get_uirev(self):
        return self._ui_revision
    uiRevision = Property(int, _get_uirev, notify=uiRevisionChanged)

    def _get_busy(self):
        return self._busy
    busy = Property(bool, _get_busy, notify=busyChanged)

    def _get_collapsed(self):
        return self.config.sidebar_collapsed
    sidebarCollapsed = Property(bool, _get_collapsed, notify=sidebarChanged)

    def _get_sidebar_auto(self):
        return self.config.sidebar_auto_collapse
    sidebarAutoCollapse = Property(bool, _get_sidebar_auto, notify=settingsChanged)

    def _get_language(self):
        return i18n.get_language()
    language = Property(str, _get_language, notify=settingsChanged)

    def _get_save_history(self):
        return self.config.save_terminal_history
    saveHistory = Property(bool, _get_save_history, notify=settingsChanged)

    def _get_auto_check(self):
        return self.config.auto_check_updates
    autoCheck = Property(bool, _get_auto_check, notify=settingsChanged)

    def _get_sort_mode(self):
        return self.config.manage_sort
    sortMode = Property(str, _get_sort_mode, notify=settingsChanged)

    def _get_gta_valid(self):
        return bool(self.config.gta_path) and is_gta_root(Path(self.config.gta_path))
    gtaPathValid = Property(bool, _get_gta_valid, notify=textsChanged)

    def _get_gta_path(self):
        return self.config.gta_path
    gtaPath = Property(str, _get_gta_path, notify=textsChanged)

    def _get_dlclist_path(self):
        return self.config.dlclist_xml_path
    dlclistPath = Property(str, _get_dlclist_path, notify=textsChanged)

    def _get_use_mods(self):
        return self.config.use_mods_folder
    useModsFolder = Property(bool, _get_use_mods, notify=textsChanged)

    def _get_dlclist_set(self):
        return bool(self.config.dlclist_xml_path) and Path(self.config.dlclist_xml_path).is_file()
    dlclistSet = Property(bool, _get_dlclist_set, notify=textsChanged)

    def _get_packs(self):
        return self._packs
    packs = Property("QVariantList", _get_packs, notify=modsListChanged)

    def _get_packs_count(self):
        return len(self._packs)
    packsCount = Property(int, _get_packs_count, notify=modsListChanged)

    def _get_packs_active(self):
        return sum(1 for p in self._packs if p["status"] == "active")
    packsActive = Property(int, _get_packs_active, notify=modsListChanged)

    def _get_els_sets(self):
        return self._els_sets
    elsSets = Property(int, _get_els_sets, notify=modsListChanged)

    def _get_els_groups(self):
        return self._els_view
    elsGroups = Property("QVariantList", _get_els_groups, notify=modsListChanged)

    def _get_hints(self):
        return sum(1 for p in self._packs if p["status"] in ("notinlist", "duplicate"))
    hintsCount = Property(int, _get_hints, notify=modsListChanged)

    def _get_profiles(self):
        active = self.config.active_profile
        out = []
        for p in self.config.profiles:
            dlc = list(p.get("dlc", []))
            els = list(p.get("els", []))
            out.append({
                "id": p.get("id", ""),
                "name": p.get("name", ""),
                "dlc": dlc,
                "els": els,
                "color": p.get("color", ""),
                "dlcCount": len(dlc),
                "elsCount": len(els),
                "active": p.get("id", "") == active,
            })
        return out
    profiles = Property("QVariantList", _get_profiles, notify=profilesChanged)

    def _get_active_profile(self):
        return self.config.active_profile
    activeProfile = Property(str, _get_active_profile, notify=profilesChanged)

    def _get_install_state(self):
        return self._install_state
    installState = Property(str, _get_install_state, notify=summaryChanged)

    def _get_last_summary(self):
        return self._last_summary
    lastSummary = Property(str, _get_last_summary, notify=summaryChanged)

    def _get_auto_maintain(self):
        return self.config.auto_maintain_dlclist
    autoMaintainDlclist = Property(bool, _get_auto_maintain, notify=settingsChanged)

    def _get_detect_els(self):
        return self.config.detect_els
    detectEls = Property(bool, _get_detect_els, notify=settingsChanged)

    def _get_rename_xml_to_els(self):
        return self.config.rename_xml_to_els
    renameXmlToEls = Property(bool, _get_rename_xml_to_els, notify=settingsChanged)

    def _get_pack_sort_key(self):
        return self.config.pack_sort_key
    packSortKey = Property(str, _get_pack_sort_key, notify=settingsChanged)

    def _get_pack_sort_dir(self):
        return self.config.pack_sort_dir
    packSortDir = Property(str, _get_pack_sort_dir, notify=settingsChanged)

    def _get_accent_presets(self):
        return list(theme.ACCENT_PRESETS)
    accentPresets = Property("QVariantList", _get_accent_presets, constant=True)

    @Slot(str)
    def setAccent(self, color: str) -> None:
        if not color:
            return
        self.config.accent = color
        self.config.save()
        QCoreApplication.instance().setStyleSheet("")
        self.accentChanged.emit()

    @Slot()
    def pickCustomAccent(self) -> None:
        chosen = QColorDialog.getColor(QColor(self.config.accent), None, T("settings_accent"))
        if chosen.isValid():
            self.setAccent(chosen.name())

    @Slot(str)
    def setLanguage(self, code: str) -> None:
        if not code or code == i18n.get_language():
            return
        i18n.set_language(code)
        self.config.language = code
        self.config.save()
        self._ui_revision += 1
        self.uiRevisionChanged.emit()
        self.textsChanged.emit()
        self.settingsChanged.emit()
        self.reloadMods()

    @Slot(bool)
    def setSidebarCollapsed(self, collapsed: bool) -> None:
        self.config.sidebar_collapsed = collapsed
        self.config.save()
        self.sidebarChanged.emit()

    @Slot(bool)
    def setSidebarAutoCollapse(self, on: bool) -> None:
        self.config.sidebar_auto_collapse = on
        self.config.save()
        self.settingsChanged.emit()

    @Slot(bool)
    def setSaveHistory(self, on: bool) -> None:
        self.config.save_terminal_history = on
        if not on:
            self.config.terminal_history = []
        self.config.save()
        self.settingsChanged.emit()

    @Slot(bool)
    def setAutoCheck(self, on: bool) -> None:
        self.config.auto_check_updates = on
        self.config.save()
        self.settingsChanged.emit()

    @Slot(bool)
    def setAutoMaintainDlclist(self, on: bool) -> None:
        self.config.auto_maintain_dlclist = on
        self.config.save()
        self.settingsChanged.emit()

    @Slot(bool)
    def setDetectEls(self, on: bool) -> None:
        self.config.detect_els = on
        self.config.save()
        self.settingsChanged.emit()

    @Slot(bool)
    def setRenameXmlToEls(self, on: bool) -> None:
        self.config.rename_xml_to_els = on
        self.config.save()
        self.settingsChanged.emit()
        self.renameChanged.emit()

    @Slot(str, str)
    def setPackSort(self, key: str, direction: str) -> None:
        if key in ("name", "added", "status"):
            self.config.pack_sort_key = key
        if direction in ("asc", "desc"):
            self.config.pack_sort_dir = direction
        self.config.save()

    @Slot(bool)
    def setUseModsFolder(self, on: bool) -> bool:
        if not on:
            if not self._confirm(T("direct_warning_title"), T("direct_warning_body"),
                                  confirm_label=T("yes"), danger=True):
                self.textsChanged.emit()
                return False
            self._log("INFO", "info", T("direct_enabled"))
        else:
            self._log("INFO", "info", T("safe_enabled"))
        self.config.use_mods_folder = on
        self.config.save()
        self.textsChanged.emit()
        return True

    @Slot()
    def chooseGtaPath(self) -> None:
        chosen = QFileDialog.getExistingDirectory(None, T("choose_gta_dialog"))
        if not chosen:
            return
        path = Path(chosen)
        if not is_gta_root(path):
            self._info(T("invalid_folder_title"), T("invalid_folder_body"))
            return
        self.config.gta_path = str(path)
        self.config.save()
        self.textsChanged.emit()
        self.renameChanged.emit()
        self._log("INFO", "ok", T("gta_path_set", path=str(path)))
        self.reloadMods()

    @Slot()
    def chooseDlclist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(None, T("choose_dlclist_dialog"), "", "XML (*.xml)")
        if not path:
            return
        self.config.dlclist_xml_path = path
        self.config.save()
        self.textsChanged.emit()
        self._log("XML", "ok", T("dlclist_set", path=path))
        self.reloadMods()

    @Slot()
    def clearDlclist(self) -> None:
        self.config.dlclist_xml_path = ""
        self.config.save()
        self.textsChanged.emit()
        self.reloadMods()

    def _paths(self):
        gta = self.config.gta_path
        if not gta or not is_gta_root(Path(gta)):
            return None
        return derive_paths(Path(gta), use_mods=self.config.use_mods_folder)

    @staticmethod
    def _fmt_ts(ts: float) -> str:
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        except (OSError, OverflowError, ValueError):
            return ""

    @Slot()
    def reloadMods(self) -> None:
        self._scan_installed()
        self._recompute()

    def _scan_installed(self) -> None:
        self._installed = []
        self._els_sets = 0
        self._els_view = []
        paths = self._paths()
        if paths is None:
            return
        self._scan_els(paths["els_root"])
        self._installed = list_installed_dlc_info(paths["dlcpacks"])

    def _scan_els(self, els_root: Path) -> None:
        groups = group_els_by_install_time(list_installed_els(els_root))
        self._els_sets = len(groups)
        view = []
        for idx, grp in enumerate(groups):
            min_mtime = min(f.mtime for f in grp)
            view.append({
                "id": f"{int(min_mtime)}-{idx}",
                "name": derive_group_name([f.name for f in grp]),
                "added": self._fmt_ts(min_mtime),
                "count": len(grp),
                "files": [
                    {
                        "name": f.name,
                        "added": self._fmt_ts(f.mtime),
                        "path": str(f.path),
                    }
                    for f in sorted(grp, key=lambda f: f.name.lower())
                ],
            })
        self._els_view = view

    def _recompute(self) -> None:
        if self._installed is None:
            self._scan_installed()
        self._packs = []
        if self._paths() is None:
            self.modsListChanged.emit()
            return

        xml_path = self.config.dlclist_xml_path
        text = ""
        if xml_path and Path(xml_path).is_file():
            try:
                text = Path(xml_path).read_text(encoding="utf-8")
            except OSError:
                text = ""
        disabled = set(dlclist.list_disabled_entries(text))
        active = set(dlclist.list_active_entries(text))
        dupes = set(dlclist.find_duplicate_entries(text))

        for name in sorted(dupes):
            if name not in self._warned_dupes:
                self._log("XML", "err", T("dlclist_duplicate", name=name))
                self._warned_dupes.add(name)

        imports = self.config.import_dates
        for d in self._installed:
            if d.name in dupes:
                status = "duplicate"
            elif d.name in disabled:
                status = "disabled"
            elif d.name in active:
                status = "active"
            else:
                status = "notinlist"
            added_ts = imports.get(d.name, d.created)
            self._packs.append({
                "name": d.name,
                "created": self._fmt_ts(d.created),
                "added": self._fmt_ts(added_ts),
                "status": status,
            })
        self.modsListChanged.emit()

    def _record_import(self, name: str) -> None:
        self.config.import_dates[name] = time.time()
        self.config.save()

    def _xml_path(self):
        p = self.config.dlclist_xml_path
        return Path(p) if p and Path(p).is_file() else None

    def _toggle_one(self, path: Path, name: str) -> None:
        active = set(dlclist.list_active_entries(path.read_text(encoding="utf-8")))
        try:
            if name in active:
                if dlclist.disable_in_file(path, name):
                    self._log("XML", "ok", T("dlclist_disabled", name=name))
            else:
                changed = dlclist.enable_in_file(path, name)
                if not changed:
                    changed = dlclist.update_file(path, name)
                if changed:
                    self._log("XML", "ok", T("dlclist_enabled", name=name))
        except Exception as exc:
            self._log("XML", "err", T("dlclist_error", err=str(exc)))

    @Slot(str)
    def toggleMod(self, name: str) -> None:
        path = self._xml_path()
        if path is None:
            return
        self._toggle_one(path, name)
        self._recompute()

    @Slot("QVariantList")
    def toggleMods(self, names) -> None:
        path = self._xml_path()
        if path is None:
            return
        for name in names:
            self._toggle_one(path, str(name))
        self._recompute()

    def _remove_one(self, paths, name: str) -> None:
        result = uninstall_dlc(name, paths["dlcpacks"], self._group_logger("DLC"))
        self._log("DLC", "ok" if result.ok else "err", result.message)
        xml = self._xml_path()
        if result.ok:
            self.config.import_dates.pop(name, None)
            if xml is not None:
                try:
                    if dlclist.remove_from_file(xml, name):
                        self._log("XML", "ok", T("dlclist_entry_removed", name=name))
                except Exception as exc:
                    self._log("XML", "err", T("dlclist_error", err=str(exc)))

    @Slot(str)
    def removeMod(self, name: str) -> None:
        paths = self._paths()
        if paths is None:
            return
        if not self._confirm(T("manage_confirm_title"), T("manage_confirm_body", name=name),
                             confirm_label=T("manage_remove_btn"), danger=True):
            return
        self._remove_one(paths, name)
        self.config.save()
        self.reloadMods()

    @Slot("QVariantList")
    def removeMods(self, names) -> None:
        paths = self._paths()
        if paths is None:
            return
        names = [str(n) for n in names]
        if not names:
            return
        body = (T("manage_confirm_body", name=names[0]) if len(names) == 1
                else T("manage_confirm_body", name=", ".join(names)))
        if not self._confirm(T("manage_confirm_title"), body,
                             confirm_label=T("manage_remove_btn"), danger=True):
            return
        for name in names:
            self._remove_one(paths, name)
        self.config.save()
        self.reloadMods()

    @Slot("QVariantList")
    def removeElsFiles(self, paths) -> None:
        paths = [str(p) for p in paths]
        if not paths:
            return
        if len(paths) == 1:
            body = T("els_remove_confirm_one", name=Path(paths[0]).name)
        else:
            body = T("els_remove_confirm_many", n=len(paths))
        if not self._confirm(T("els_remove_title"), body,
                             confirm_label=T("manage_remove_btn"), danger=True):
            return
        for p in paths:
            fp = Path(p)
            try:
                if fp.is_file():
                    fp.unlink()
                    self._log("ELS", "ok", T("els_file_removed", name=fp.name))
            except OSError as exc:
                self._log("ELS", "err", T("els_remove_failed", name=fp.name, err=str(exc)))
        self.reloadMods()

    @Slot("QVariantList")
    def setOrder(self, names) -> None:
        xml = self._xml_path()
        if xml is None:
            return
        try:
            dlclist.set_order_in_file(xml, [str(n) for n in names])
        except Exception as exc:
            self._log("XML", "err", T("dlclist_error", err=str(exc)))
        self.reloadMods()

    @Slot()
    def repair(self) -> None:
        paths = self._paths()
        xml = self._xml_path()
        if paths is None or xml is None:
            return
        text = xml.read_text(encoding="utf-8")
        registered = set(dlclist.list_entries(text))
        installed = {d.name for d in list_installed_dlc_info(paths["dlcpacks"])}
        orphans = sorted(installed - registered)
        missing = sorted(registered - installed)
        if not orphans and not missing:
            self._log("XML", "info", T("repair_none"))
            return
        added = 0
        for name in orphans:
            try:
                if dlclist.update_file(xml, name):
                    self._log("XML", "ok", T("repair_added", name=name))
                    added += 1
            except Exception as exc:
                self._log("XML", "err", T("dlclist_error", err=str(exc)))
        removed = kept = 0
        decide = ReplaceDecider(self._ask, "repair_missing_body",
                                offer_all=len(missing) > 1, title_key="repair_missing_title")
        for name in missing:
            if not decide(name):
                kept += 1
                continue
            try:
                if dlclist.remove_from_file(xml, name):
                    self._log("XML", "ok", T("repair_removed", name=name))
                    removed += 1
            except Exception as exc:
                self._log("XML", "err", T("dlclist_error", err=str(exc)))
        self._log("XML", "info", T("repair_summary", added=added, removed=removed, kept=kept))
        self.reloadMods()

    def _find_profile(self, pid: str):
        if not pid:
            return None
        for p in self.config.profiles:
            if p.get("id") == pid:
                return p
        return None

    def _stash_profile(self, prof) -> None:
        if prof is None:
            return
        paths = self._paths()
        if paths is None:
            return
        name = prof.get("name", "")
        profiles.stash_els(
            paths["els_root"], name, prof.get("els", []),
            log=lambda n: self._log("ELS", "ok", T("profile_els_stashed", n=n, name=name)),
        )
        xml = self._xml_path()
        if xml is not None and prof.get("dlc"):
            try:
                if dlclist.comment_profile_in_file(xml, prof["id"], name, prof["dlc"]):
                    self._log("XML", "ok", T("profile_dlc_commented", name=name))
            except Exception as exc:
                self._log("XML", "err", T("dlclist_error", err=str(exc)))

    def _unstash_profile(self, prof, paths) -> None:
        if prof is None:
            return
        name = prof.get("name", "")
        profiles.restore_els(
            paths["els_root"], name,
            log=lambda n: self._log("ELS", "ok", T("profile_els_restored", n=n, name=name)),
        )
        xml = self._xml_path()
        if xml is not None:
            try:
                if dlclist.uncomment_profile_in_file(xml, prof["id"]):
                    self._log("XML", "ok", T("profile_dlc_uncommented", name=name))
            except Exception as exc:
                self._log("XML", "err", T("dlclist_error", err=str(exc)))

    def _apply_profile(self, pid: str) -> None:
        paths = self._paths()
        if paths is None:
            self._info(T("gta_missing_title"), T("gta_missing_body"))
            return
        prof = self._find_profile(pid)
        if prof is None:
            return
        self._set_busy(True)
        try:
            current = self.config.active_profile
            if current and current != pid:
                self._stash_profile(self._find_profile(current))
            self._unstash_profile(prof, paths)
            self.config.active_profile = pid
            self.config.save()
            self._log("INFO", "ok", T("profile_activated", name=prof.get("name", "")))
        finally:
            self._set_busy(False)
        self.profilesChanged.emit()
        self.reloadMods()

    def _deactivate_profile(self) -> None:
        paths = self._paths()
        if paths is None:
            return
        prof = self._find_profile(self.config.active_profile)
        self._set_busy(True)
        try:
            if prof is not None:
                self._stash_profile(prof)
                self._log("INFO", "ok", T("profile_deactivated", name=prof.get("name", "")))
            self.config.active_profile = ""
            self.config.save()
        finally:
            self._set_busy(False)
        self.profilesChanged.emit()
        self.reloadMods()

    @Slot(str)
    def toggleProfile(self, pid: str) -> None:
        if self.config.active_profile == pid:
            self._deactivate_profile()
        else:
            self._apply_profile(pid)

    @Slot(str, "QVariantList", "QVariantList", str, str)
    def saveProfile(self, name, dlc_names, els_names, color, edit_id) -> None:
        name = str(name).strip()
        if not name:
            return
        dlc = [str(x) for x in dlc_names]
        els = [str(x) for x in els_names]
        color = str(color).strip()
        edit_id = str(edit_id)
        found = self._find_profile(edit_id) if edit_id else None
        if found is not None:
            found["name"], found["dlc"], found["els"] = name, dlc, els
            found["color"] = color
            self._log("INFO", "ok", T("profile_saved", name=name))
        else:
            pid = str(int(time.time() * 1000))
            self.config.profiles.append(
                {"id": pid, "name": name, "dlc": dlc, "els": els, "color": color})
            self._log("INFO", "ok", T("profile_created", name=name))
        self.config.save()
        self.profilesChanged.emit()
        if found is not None and edit_id == self.config.active_profile:
            self._apply_profile(edit_id)

    @Slot(str)
    def deleteProfile(self, pid: str) -> None:
        prof = self._find_profile(pid)
        if prof is None:
            return
        if not self._confirm(T("profile_delete_title"),
                             T("profile_delete_body", name=prof.get("name", "")),
                             confirm_label=T("manage_remove_btn"), danger=True):
            return
        paths = self._paths()
        if paths is not None:
            self._unstash_profile(prof, paths)
        if self.config.active_profile == pid:
            self.config.active_profile = ""
        self.config.profiles = [p for p in self.config.profiles if p.get("id") != pid]
        self.config.save()
        self.profilesChanged.emit()
        self.reloadMods()
        self._log("INFO", "ok", T("profile_deleted", name=prof.get("name", "")))

    def _default_zones(self) -> list:
        return [{
            "id": "auto", "name": T("zone_default_name"), "auto": True,
            "rel": "", "color": "", "col": 0, "row": 0, "w": 2, "h": 2,
        }]

    def _zones(self) -> list:
        return self.config.drop_zones or self._default_zones()

    def _find_zone(self, zone_id: str):
        for z in self._zones():
            if z.get("id") == zone_id:
                return z
        return None

    def _zone_target(self, zone):
        gta = self.config.gta_path
        if not gta:
            return None
        root = Path(gta).resolve()
        rel = (zone.get("rel") or "").strip().replace("\\", "/")
        try:
            target = (root / rel).resolve()
            target.relative_to(root)
        except (ValueError, OSError):
            return None
        return target

    def _get_drop_zones(self):
        out = []
        for z in self._zones():
            auto = bool(z.get("auto"))
            rel = z.get("rel") or ""
            target = None if auto else self._zone_target(z)
            out.append({
                "id": z.get("id", ""),
                "name": z.get("name", ""),
                "auto": auto,
                "rel": rel,
                "color": z.get("color") or "",
                "col": int(z.get("col", 0)),
                "row": int(z.get("row", 0)),
                "w": int(z.get("w", 1)),
                "h": int(z.get("h", 1)),
                "targetLabel": T("zone_target_root") if (not auto and rel == "") else rel,
                "valid": auto or target is not None,
                "exists": True if auto else bool(target and target.is_dir()),
            })
        return out
    dropZones = Property("QVariantList", _get_drop_zones, notify=zonesChanged)

    def _get_zone_presets(self):
        presets = []
        seen = set()

        def add(label, rel):
            rel = (rel or "").replace("\\", "/")
            if rel not in seen:
                seen.add(rel)
                presets.append({"label": label, "rel": rel})

        gta = self.config.gta_path
        if gta and is_gta_root(Path(gta)):
            root = Path(gta).resolve()
            paths = derive_paths(root, use_mods=self.config.use_mods_folder)

            def rel_of(p):
                try:
                    return Path(p).resolve().relative_to(root).as_posix()
                except (ValueError, OSError):
                    return ""

            add("DLC Packs", rel_of(paths["dlcpacks"]))
            add("ELS", rel_of(paths["els_root"]))
            if self.config.use_mods_folder:
                add("mods", rel_of(paths["mods_root"]))
        add("scripts", "scripts")
        return presets
    zonePresets = Property("QVariantList", _get_zone_presets, notify=textsChanged)

    @Slot("QVariant")
    def saveZone(self, spec) -> None:
        if not isinstance(spec, dict):
            return
        auto = bool(spec.get("auto"))
        name = (spec.get("name") or "").strip()
        if not name:
            name = T("zone_default_name") if auto else T("zone_editor_new_title")
        rel = "" if auto else (spec.get("rel") or "").strip().replace("\\", "/")

        def clampi(v, lo, hi, default):
            try:
                v = int(v)
            except (TypeError, ValueError):
                return default
            return max(lo, min(hi, v))

        col = clampi(spec.get("col"), 0, 1, 0)
        row = clampi(spec.get("row"), 0, 1, 0)
        w = clampi(spec.get("w"), 1, 2, 1)
        h = clampi(spec.get("h"), 1, 2, 1)
        w = min(w, 2 - col)
        h = min(h, 2 - row)
        zone = {
            "id": (spec.get("id") or "").strip() or uuid.uuid4().hex[:8],
            "name": name, "auto": auto, "rel": rel,
            "color": (spec.get("color") or ""),
            "col": col, "row": row, "w": w, "h": h,
        }
        zones = [dict(z) for z in self._zones()]
        existing = next((z for z in zones if z.get("id") == zone["id"]), None)
        if existing is None:
            if len(zones) >= 4:
                return
            zones.append(zone)
        else:
            existing.update(zone)
        self.config.drop_zones = zones
        self.config.save()
        self.zonesChanged.emit()

    @Slot(str)
    def removeZone(self, zone_id: str) -> None:
        zones = [dict(z) for z in self._zones() if z.get("id") != zone_id]
        self.config.drop_zones = zones
        self.config.save()
        self.zonesChanged.emit()

    @Slot()
    def resetZones(self) -> None:
        self.config.drop_zones = []
        self.config.save()
        self.zonesChanged.emit()

    @Slot(result=str)
    def chooseZoneFolder(self) -> str:
        gta = self.config.gta_path
        if not gta or not is_gta_root(Path(gta)):
            self._info(T("zone_no_path_title"), T("zone_no_path_body"))
            return ""
        root = Path(gta).resolve()
        chosen = QFileDialog.getExistingDirectory(None, T("zone_choose_folder"), str(root))
        if not chosen:
            return ""
        try:
            rel = Path(chosen).resolve().relative_to(root)
        except ValueError:
            self._info(T("zone_outside_title"), T("zone_outside_body"))
            return ""
        rel_str = rel.as_posix()
        return "" if rel_str == "." else rel_str

    @Slot(str)
    def openZoneFolder(self, zone_id: str) -> None:
        zone = self._find_zone(zone_id)
        if zone is None:
            return
        if zone.get("auto"):
            paths = self._paths()
            target = paths["dlcpacks"] if paths else None
        else:
            target = self._zone_target(zone)
        if target is None:
            self._info(T("zone_no_target_title"), T("zone_no_target_body"))
            return
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    @Slot(str, "QVariantList")
    def dropToZone(self, zone_id, urls) -> None:
        zone = self._find_zone(zone_id)
        if zone is None or zone.get("auto"):
            self.handleDrop(urls)
            return
        self._install_to_zone(self._urls_to_paths(urls), zone)

    def _install_to_zone(self, srcs, zone) -> None:
        if self._busy:
            return
        if not srcs:
            self._log("INFO", "err", T("zone_nothing"))
            return
        if self._paths() is None:
            self._info(T("gta_missing_title"), T("gta_missing_body"))
            return
        target = self._zone_target(zone)
        if target is None:
            self._info(T("zone_no_target_title"), T("zone_no_target_body"))
            return

        group = "COPY"
        self._install_state = "running"
        self._last_summary = ""
        self.summaryChanged.emit()
        self._set_busy(True)
        ok = 0
        try:
            target.mkdir(parents=True, exist_ok=True)
            decide = ReplaceDecider(self._ask, "zone_replace_body", offer_all=len(srcs) > 1)
            log = self._group_logger(group)
            progress = lambda done, total, n: self._show_progress(group, done, total, n)
            for src in srcs:
                if not src.exists():
                    self._log(group, "err", T("els_src_missing", path=str(src)))
                    continue
                try:
                    result = install_path(src, target, log, progress=progress)
                    if result.conflict:
                        if not decide(src.name):
                            self._log(group, "info", T("zone_kept", name=src.name))
                            continue
                        result = install_path(src, target, log, overwrite=True, progress=progress)
                    self._log(group, "ok" if result.ok else "err", result.message)
                    if result.ok:
                        ok += 1
                except Exception as exc:
                    self._log(group, "err", T("unexpected_error", err=str(exc)))
        finally:
            self.progress.emit(-1.0, "")
            self._set_busy(False)
        self._install_state = "done"
        self._last_summary = T("zone_summary", n=ok, name=zone.get("name", ""))
        self.summaryChanged.emit()
        self.reloadMods()

    def _rename_presets(self) -> list:
        return self.config.rename_presets or [
            {"id": f"std-{model}", "name": name, "model": model}
            for name, model in renamer.DEFAULT_PRESETS
        ]

    def _get_rename_presets(self):
        return [
            {"id": p.get("id", ""), "name": p.get("name", ""), "model": p.get("model", "")}
            for p in self._rename_presets()
        ]
    renamePresets = Property("QVariantList", _get_rename_presets, notify=renamePresetsChanged)

    def _get_rename_groups(self):
        groups = renamer.group_by_base(self._rename_files)
        return [
            {"base": base, "count": len(files)}
            for base, files in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        ]
    renameGroups = Property("QVariantList", _get_rename_groups, notify=renameChanged)

    def _get_rename_base(self):
        return self._rename_base
    renameBase = Property(str, _get_rename_base, notify=renameChanged)

    def _get_rename_files(self):
        out = []
        for f in self._rename_files:
            if not renamer.is_renameable(f):
                continue
            base, suffix = renamer.split_stem(f.stem)
            if base.lower() != self._rename_base:
                continue
            out.append({"name": f.name, "suffix": suffix, "ext": f.suffix.lower()})
        return out
    renameFiles = Property("QVariantList", _get_rename_files, notify=renameChanged)

    def _get_rename_skipped(self):
        skipped = 0
        for f in self._rename_files:
            if not renamer.is_renameable(f):
                skipped += 1
                continue
            base, _ = renamer.split_stem(f.stem)
            if base.lower() != self._rename_base:
                skipped += 1
        return skipped
    renameSkipped = Property(int, _get_rename_skipped, notify=renameChanged)

    def _get_rename_dest(self):
        return self.config.rename_last_dest
    renameDest = Property(str, _get_rename_dest, notify=renameChanged)

    def _rename_selected(self) -> list:
        out = []
        for f in self._rename_files:
            if not renamer.is_renameable(f):
                continue
            base, _ = renamer.split_stem(f.stem)
            if base.lower() == self._rename_base:
                out.append(f)
        return out

    def _rename_els_dir(self):
        if not self.config.rename_xml_to_els:
            return None
        paths = self._paths()
        if paths is None:
            return None
        return paths["root"] / "ELS" / "pack_default"

    def _rename_routes_to_els(self, f: Path) -> bool:
        return renamer.routes_to_els(
            f, self.config.rename_xml_to_els, self._rename_els_dir() is not None,
            is_els_xml=lambda p: self._rename_els_like.get(str(p), False),
        )

    def _get_rename_needs_dest(self):
        files = self._rename_selected()
        if not files:
            return True
        return any(not self._rename_routes_to_els(f) for f in files)
    renameNeedsDest = Property(bool, _get_rename_needs_dest, notify=renameChanged)

    def _get_rename_state(self):
        return self._rename_state
    renameState = Property(str, _get_rename_state, notify=renameChanged)

    def _get_rename_summary(self):
        return self._rename_summary
    renameSummary = Property(str, _get_rename_summary, notify=renameChanged)

    def _set_rename_sources(self, srcs) -> None:
        files = renamer.collect_files(srcs)
        if not files:
            self._log("REN", "err", T("rename_nothing"))
            return
        self._rename_files = files
        self._rename_base = renamer.detect_base(files)
        self._rename_els_like = {
            str(f): bool(list_els_xmls(f))
            for f in files if f.suffix.lower() == ".xml"
        }
        groups = renamer.group_by_base(files)
        if not groups:
            self._log("REN", "err", T("rename_no_model_files"))
        elif len(groups) > 1:
            self._log("REN", "info", T("rename_multi_log", n=len(groups)))
        else:
            self._log("REN", "ok", T("rename_detected", base=self._rename_base,
                                     n=len(groups[self._rename_base])))
        self.renameChanged.emit()

    @Slot("QVariantList")
    def renameDrop(self, urls) -> None:
        self._set_rename_sources(self._urls_to_paths(urls))

    @Slot()
    def renameChooseFiles(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            None, T("rename_choose_files_dialog"), "",
            "GTA vehicle files (*.yft *.ytd *.xml);;All files (*)",
        )
        if files:
            self._set_rename_sources([Path(f) for f in files])

    @Slot(str)
    def renameSelectBase(self, base: str) -> None:
        self._rename_base = str(base).lower()
        self.renameChanged.emit()

    @Slot()
    def renameClear(self) -> None:
        self._rename_files = []
        self._rename_base = ""
        self._rename_els_like = {}
        self.renameChanged.emit()

    @Slot()
    def renameChooseDest(self) -> None:
        chosen = QFileDialog.getExistingDirectory(
            None, T("rename_dest_choose_dialog"), self.config.rename_last_dest or "")
        if not chosen:
            return
        self.config.rename_last_dest = str(Path(chosen))
        self.config.save()
        self.renameChanged.emit()

    @Slot(str)
    def renameExecute(self, model: str) -> None:
        if self._busy:
            return
        if not self._rename_files or not self._rename_base:
            self._info(T("rename_no_files_title"), T("rename_no_files_body"))
            return
        model = renamer.sanitize_model(model)
        if not model:
            self._info(T("rename_no_target_title"), T("rename_no_target_body"))
            return
        plan = renamer.plan_renames(self._rename_files, self._rename_base, model)
        if not plan:
            self._info(T("rename_no_files_title"), T("rename_no_files_body"))
            return

        els_dir = self._rename_els_dir()
        jobs = [(src, new_name, self._rename_routes_to_els(src)) for src, new_name in plan]
        els_fallback = (self.config.rename_xml_to_els and els_dir is None
                        and any(src.suffix.lower() == ".xml" for src, _, _ in jobs))

        dest = self.config.rename_last_dest
        dest_dir = Path(dest) if dest and Path(dest).is_dir() else None
        if dest_dir is None and any(not to_els for _, _, to_els in jobs):
            self._info(T("rename_no_dest_title"), T("rename_no_dest_body"))
            return

        group = "REN"
        self._rename_state = "running"
        self._rename_summary = ""
        self.renameChanged.emit()
        self._set_busy(True)
        ok = els_ok = 0
        try:
            if els_fallback:
                self._log(group, "info", T("rename_els_fallback"))
            if any(to_els for _, _, to_els in jobs):
                try:
                    els_dir.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    self._log(group, "err", T("rename_copy_failed",
                                              name=str(els_dir), err=str(exc)))
            decide = ReplaceDecider(self._ask, "zone_replace_body", offer_all=len(jobs) > 1)
            total = len(jobs)
            for done, (src, new_name, to_els) in enumerate(jobs):
                self._show_progress(group, done, total, src.name)
                if not src.is_file():
                    self._log(group, "err", T("els_src_missing", path=str(src)))
                    continue
                target = (els_dir if to_els else dest_dir) / new_name
                try:
                    if target.exists() and src.resolve() == target.resolve():
                        self._log(group, "info", T("rename_same_file", name=src.name))
                        continue
                except OSError:
                    pass
                if target.exists() and not decide(new_name):
                    self._log(group, "info", T("zone_kept", name=new_name))
                    continue
                try:
                    shutil.copy2(src, target)
                    ok += 1
                    if to_els:
                        els_ok += 1
                        self._log(group, "ok", T("rename_copied_els", old=src.name, new=new_name))
                    else:
                        self._log(group, "ok", T("rename_copied", old=src.name, new=new_name))
                except OSError as exc:
                    self._log(group, "err", T("rename_copy_failed", name=src.name, err=str(exc)))
            self._show_progress(group, total, total, "")
        finally:
            self.progress.emit(-1.0, "")
            self._set_busy(False)
        self._rename_state = "done"
        self._rename_summary = (T("rename_done_summary_els", n=ok, els=els_ok) if els_ok
                                else T("rename_done_summary", n=ok))
        self.renameChanged.emit()
        if els_ok:
            self.reloadMods()

    @Slot("QVariant")
    def saveRenamePreset(self, spec) -> None:
        if not isinstance(spec, dict):
            return
        name = (spec.get("name") or "").strip()
        model = renamer.sanitize_model(spec.get("model") or "")
        if not name or not model:
            return
        presets = [dict(p) for p in self._rename_presets()]
        pid = (spec.get("id") or "").strip() or uuid.uuid4().hex[:8]
        entry = {"id": pid, "name": name, "model": model}
        existing = next((p for p in presets if p.get("id") == pid), None)
        if existing is None:
            presets.append(entry)
        else:
            existing.update(entry)
        self.config.rename_presets = presets
        self.config.save()
        self.renamePresetsChanged.emit()

    @Slot(str)
    def removeRenamePreset(self, pid: str) -> None:
        presets = [dict(p) for p in self._rename_presets() if p.get("id") != pid]
        self.config.rename_presets = presets
        self.config.save()
        self.renamePresetsChanged.emit()

    @staticmethod
    def _urls_to_paths(urls) -> list:
        srcs = []
        for u in urls:
            s = u.toLocalFile() if isinstance(u, QUrl) else str(u)
            if s.startswith("file:"):
                s = QUrl(s).toLocalFile()
            if s:
                srcs.append(Path(s))
        return srcs

    @Slot("QVariantList")
    def handleDrop(self, urls) -> None:
        self._install_sources(self._urls_to_paths(urls))

    @Slot()
    def chooseArchives(self) -> None:
        if self._busy:
            return
        files, _ = QFileDialog.getOpenFileNames(
            None, T("choose_archives_dialog"), "",
            "Archives (*.zip *.rar *.7z *.oiv)",
        )
        if files:
            self._install_sources([Path(f) for f in files])

    def _install_sources(self, srcs) -> None:
        if self._busy:
            return
        if not srcs:
            self._log("INFO", "err", T("drop_nothing"))
            return
        paths = self._paths()
        if paths is None:
            self._info(T("gta_missing_title"), T("gta_missing_body"))
            return

        self._install_state = "running"
        self._last_summary = ""
        self.summaryChanged.emit()
        self._set_busy(True)
        started = time.time()
        dlc_ok = els_ok = 0
        temp_dirs: list[Path] = []
        try:
            scan_items = self._expand_sources(srcs, temp_dirs)
            dlc_packs: list[Path] = []
            els_jobs: list[tuple[Path, list[Path]]] = []
            unknown: list[str] = []
            for path, display, deep in scan_items:
                if deep:
                    packs = find_dlc_packs_deep(path)
                    has_els = self.config.detect_els and bool(list_els_xmls(path))
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
                    elif self.config.detect_els and is_els_source(path):
                        els_jobs.append((path, []))
                    else:
                        unknown.append(display)

            els_srcs: list[Path] = []
            for path, packs in els_jobs:
                chosen = self._resolve_els_source(path, packs)
                if chosen is not None:
                    els_srcs.append(chosen)

            els_count = sum(len(list_els_xmls(s)) for s in els_srcs)
            dlc_decide = ReplaceDecider(self._ask, "dlc_replace_body", offer_all=len(dlc_packs) > 1)
            els_decide = ReplaceDecider(self._ask, "els_replace_body", offer_all=els_count > 1)

            for pack in dlc_packs:
                try:
                    if self._install_dlc_pack(pack, paths, dlc_decide):
                        dlc_ok += 1
                except Exception as exc:
                    self._log("DLC", "err", T("unexpected_error", err=str(exc)))
            for src in els_srcs:
                try:
                    if self._install_els_src(src, paths, els_decide):
                        els_ok += 1
                except Exception as exc:
                    self._log("ELS", "err", T("unexpected_error", err=str(exc)))
            for name in unknown:
                self._log("INFO", "err", T("drop_unknown", name=name))
        finally:
            self.progress.emit(-1.0, "")
            self._set_busy(False)
            for d in temp_dirs:
                shutil.rmtree(d, ignore_errors=True)
        secs = f"{time.time() - started:.1f}"
        self._install_state = "done"
        self._last_summary = T("install_summary", packs=dlc_ok, els=els_ok, secs=secs)
        self.summaryChanged.emit()
        self.reloadMods()

    def _expand_sources(self, srcs, temp_dirs):
        items = []
        for src in srcs:
            if not archive.is_archive(src):
                items.append((src, src.name, False))
                continue
            self._log("INFO", "work", T("archive_extracting", name=src.name))
            try:
                dest = archive.extract_to_temp(src)
            except archive.CorruptArchive:
                self._log("INFO", "err", T("archive_corrupt", name=src.name))
                continue
            except archive.UnsupportedArchive as exc:
                self._log("INFO", "err", T("archive_unsupported", name=src.name, fmt=str(exc)))
                continue
            except archive.ArchiveError as exc:
                self._log("INFO", "err", T("archive_failed", name=src.name, err=str(exc)))
                continue
            temp_dirs.append(dest.parent)
            self._log("INFO", "ok", T("archive_extracted", name=src.name))
            items.append((dest, src.name, True))
        return items

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.busyChanged.emit()

    def _install_dlc_pack(self, pack, paths, decide) -> bool:
        log = self._group_logger("DLC")
        progress = lambda done, total, name: self._show_progress("DLC", done, total, name)
        result = install_dlc(pack, paths["dlcpacks"], log, progress=progress)
        if result.conflict:
            if not decide(pack.name):
                self._log("DLC", "info", T("dlc_kept", name=pack.name))
                return False
            result = install_dlc(pack, paths["dlcpacks"], log, overwrite=True, progress=progress)
        self._log("DLC", "ok" if result.ok else "err", result.message)
        if result.ok and result.dlc_name:
            self._record_import(result.dlc_name)
            if self.config.auto_maintain_dlclist:
                self._handle_dlclist_update(result.dlc_name)
        return result.ok

    def _resolve_els_source(self, src, pack_folders):
        groups = group_els_by_folder(src)
        if len(groups) <= 1 or not els_has_name_collision(groups):
            return src
        if not pack_folders:
            pack_folders = find_dlc_packs_deep(src)
        default = closest_els_folder(sorted(groups), pack_folders)
        options = []
        for folder in sorted(groups, key=lambda f: str(f).lower()):
            try:
                rel = folder.relative_to(src)
                label = T("els_pick_root") if str(rel) == "." else str(rel)
            except ValueError:
                label = folder.name
            note = T("els_pick_count", n=len(groups[folder]))
            if folder == default:
                note += "  ·  " + T("els_pick_recommended")
            options.append({"value": str(folder), "label": label, "note": note})
        chosen = self._pick(T("els_pick_title"), T("els_pick_hint"), options, str(default))
        if not chosen:
            self._log("ELS", "info", T("els_variant_skipped"))
            return None
        chosen_path = Path(chosen)
        self._log("ELS", "info", T("els_variant_chosen", folder=chosen_path.name))
        return chosen_path

    def _install_els_src(self, src, paths, decide) -> bool:
        log = self._group_logger("ELS")
        progress = lambda done, total, name: self._show_progress("ELS", done, total, name)
        target = paths["root"] / "ELS" / "pack_default"
        result = install_els(src, target, log, resolve=decide, progress=progress)
        self._log("ELS", "ok" if result.ok else "err", result.message)
        return result.ok

    def _handle_dlclist_update(self, dlc_name: str) -> None:
        xml = self.config.dlclist_xml_path
        if xml and Path(xml).is_file():
            try:
                changed = dlclist.update_file(Path(xml), dlc_name)
            except Exception as exc:
                self._log("XML", "err", T("dlclist_error", err=str(exc)))
                return
            if changed:
                self._log("XML", "ok", T("dlclist_added", name=dlc_name))
            else:
                self._log("XML", "info", T("dlclist_existed", name=dlc_name))
            return
        entry = f"    <Item>dlcpacks:/{dlc_name}/</Item>"
        self._log("XML", "info", T("dlclist_hint_no_xml", entry=entry))

    @Slot(bool)
    def checkUpdates(self, manual: bool) -> None:
        from PySide6.QtCore import QThread

        class _Worker(QThread):
            done = Signal(bool, object)

            def run(self):
                try:
                    self.done.emit(True, updater.check_for_update())
                except Exception:
                    self.done.emit(False, None)

        if self._update_thread is not None and self._update_thread.isRunning():
            return
        w = _Worker()
        w.done.connect(lambda ok, info: self._on_update_result(ok, info, manual))
        self._update_thread = w
        w.start()

    def _on_update_result(self, ok, info, manual) -> None:
        if not ok:
            if manual:
                self._info(T("settings_title"), T("update_check_failed"))
            return
        if info is None:
            if manual:
                self._info(T("settings_title"),
                           T("update_none", current=updater.CURRENT_VERSION))
            return
        self._prompt_update(info)

    def _prompt_update(self, info) -> None:
        self._log("INFO", "info", T("update_available_log", version=info.version))
        choice = self._choose(
            T("update_available_title"),
            T("update_available_body", version=info.version, current=updater.CURRENT_VERSION),
            [
                {"id": "never", "label": T("update_never_btn"), "kind": "ghost"},
                {"id": "later", "label": T("update_later_btn"), "kind": "ghost"},
                {"id": "install", "label": T("update_install_btn"), "kind": "solid"},
            ],
            cancel_id="later",
        )
        if choice == "install":
            self._download_update(info)
        elif choice == "never":
            self.config.auto_check_updates = False
            self.config.save()
            self.settingsChanged.emit()

    def _download_update(self, info) -> None:
        if not info.asset_url:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(info.page_url))
            return
        try:
            self._log("INFO", "work", T("update_downloading"))
            path = updater.download_installer(
                info, progress=lambda d, t: self._show_progress("INFO", d, t, T("update_downloading")))
            self.progress.emit(-1.0, "")
            updater.run_installer(path)
            QCoreApplication.quit()
        except Exception as exc:
            self.progress.emit(-1.0, "")
            self._info(T("update_available_title"),
                       T("update_download_failed", err=str(exc)))

    @Slot()
    def maybeCheckOnStart(self) -> None:
        if self.config.auto_check_updates:
            self.checkUpdates(False)
