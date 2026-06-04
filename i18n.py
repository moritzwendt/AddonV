"""Simple dict-based translator for the AddonV GUI.

`T(key, **fmt)` looks up the active language, falls back to English, and
formats positional/keyword args via str.format. Modules call `T()` lazily
so that switching language at runtime takes effect on the next render
(`MainWindow.retranslate_ui()`).
"""
from __future__ import annotations

LANGUAGES: dict[str, str] = {
    "en": "English",
    "de": "Deutsch",
    "ru": "Русский",
    "es": "Español",
}

_DEFAULT = "en"
_current = _DEFAULT


def set_language(code: str) -> None:
    global _current
    if code in LANGUAGES:
        _current = code


def get_language() -> str:
    return _current


def T(key: str, **kwargs) -> str:
    table = TRANSLATIONS.get(_current, TRANSLATIONS[_DEFAULT])
    text = table.get(key) or TRANSLATIONS[_DEFAULT].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # window / generic
        "window_title": "AddonV",
        "ok": "OK",
        "cancel": "Cancel",
        "yes": "Yes",
        "no": "No",

        # language dialog
        "lang_dialog_title": "Choose language",
        "lang_dialog_hint": "Select your preferred language:",
        "lang_button": "🌐 Language",

        # manage mods
        "manage_btn": "📦 Manage mods",
        "manage_dialog_title": "Installed DLC mods",
        "manage_empty": "No DLC mods installed.",
        "manage_remove_btn": "Remove",
        "manage_disable_btn": "Disable",
        "manage_enable_btn": "Enable",
        "manage_repair_btn": "Repair dlclist",
        "manage_state_active": "active",
        "manage_state_disabled": "disabled",
        "manage_state_unlisted": "not in dlclist",
        "manage_state_duplicate": "duplicate",
        "manage_search_placeholder": "Search mods…",
        "manage_no_matches": "No mods match your search.",
        "manage_sort_order": "Load order (dlclist)",
        "manage_close_btn": "Close",
        "manage_sort_label": "Sort by:",
        "manage_sort_name": "Name (A–Z)",
        "manage_sort_date": "Date added (newest)",
        "manage_added": "added {date}",
        "manage_confirm_title": "Remove mod?",
        "manage_confirm_body": "Remove DLC '{name}'?\n\nThe pack folder and its dlclist.xml entry will be deleted.",
        "dlc_removing": "Removing DLC '{name}'…",
        "dlc_removed": "DLC '{name}' removed.",
        "dlc_remove_failed": "Could not remove DLC '{name}': {err}",
        "dlc_not_installed": "DLC '{name}' is not installed.",
        "dlclist_entry_removed": "dlclist.xml: entry for '{name}' removed.",
        "dlclist_disabled": "dlclist.xml: '{name}' disabled (commented out).",
        "dlclist_enabled": "dlclist.xml: '{name}' enabled.",
        "dlclist_duplicate": "dlclist.xml: '{name}' is listed more than once — remove the duplicate.",

        # repair dlclist
        "repair_none": "dlclist.xml: nothing to repair — list matches installed packs.",
        "repair_added": "dlclist.xml: re-added missing entry for '{name}'.",
        "repair_removed": "dlclist.xml: removed entry for missing '{name}'.",
        "repair_missing_title": "Folder missing",
        "repair_missing_body": (
            "'{name}' is listed in dlclist.xml but its pack folder is missing.\n\n"
            "Remove the entry from dlclist.xml?"
        ),
        "repair_summary": "Repair done: {added} added, {removed} removed, {kept} kept.",

        # path / mode
        "choose_gta_btn": "Choose GTA path…",
        "gta_path_label": "GTA path:  {path}",
        "gta_path_unset": "GTA path:  (not set — please choose)",
        "mods_checkbox": "Install into /mods subfolder (recommended — keeps original files untouched)",
        "mode_safe": "Mode: safe (mods/)",
        "mode_direct": "Mode: DIRECT — original files will be modified!",

        # drop zones
        "drop_zone_title": "Drop mods here",
        "drop_zone_hint": (
            "Drag DLC folders (with dlc.rpf) or ELS-VCF .xml files/folders here.\n"
            "AddonV detects the type automatically:\n"
            "DLC → mods/update/x64/dlcpacks (+ dlclist.xml) · ELS → ELS/pack_default."
        ),
        "drop_unknown": (
            "Couldn't tell what '{name}' is — drop a DLC folder "
            "(containing dlc.rpf) or ELS-VCF .xml file(s)."
        ),

        # dlclist row
        "dlclist_btn": "Choose dlclist.xml…",
        "dlclist_clear_btn": "reset",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (optional — extracted file for automatic editing)",

        # log messages (GUI)
        "gta_detected": "GTA detected automatically: {path}",
        "gta_not_detected": "Note: GTA path not detected automatically — please choose above.",
        "gta_path_set": "GTA path set: {path}",
        "dlclist_set": "dlclist.xml set: {path}",
        "direct_enabled": "Direct installation enabled — original files will be modified.",
        "safe_enabled": "Safe installation enabled (mods/ subfolder).",
        "dlclist_added": "dlclist.xml: entry for '{name}' added.",
        "dlclist_existed": "dlclist.xml: entry for '{name}' already present.",
        "dlclist_error": "Error editing dlclist.xml: {err}",
        "dlclist_hint_no_xml": (
            "Note: no extracted dlclist.xml configured.\n"
            "  Please add the following entry to update.rpf/common/data/dlclist.xml\n"
            "  before </Paths> (e.g. via OpenIV):\n{entry}"
        ),

        # message boxes
        "gta_missing_title": "GTA path missing",
        "gta_missing_body": "Please choose the GTA installation path first.",
        "invalid_folder_title": "Invalid folder",
        "invalid_folder_body": "This folder doesn't contain GTA5.exe / GTAVLauncher.exe.",
        "choose_gta_dialog": "Choose GTA installation folder",
        "choose_dlclist_dialog": "Choose extracted dlclist.xml",
        "direct_warning_title": "Direct installation – Warning!",
        "direct_warning_body": (
            "You are about to install mods directly into the GTA main folder.\n\n"
            "Risks:\n"
            "• Original game files will be overwritten.\n"
            "• Game updates or online/anti-cheat checks may fail.\n"
            "• Broken mods can render the game unplayable.\n"
            "• Without a backup, rollback is only possible by reinstalling.\n\n"
            "The mods/ subfolder (OpenIV convention) is recommended,\n"
            "as it leaves the original files untouched.\n\n"
            "Still install directly into the GTA main folder?"
        ),

        # installer messages (DLC)
        "dlc_exists": "DLC '{name}' already exists.",
        "dlc_installing": "Installing DLC '{name}'…",
        "dlc_installed": "DLC '{name}' installed ({size}).",
        "dlc_copy_failed": (
            "Could not install DLC '{name}': {err}\n"
            "  (Tip: installing into Program Files may require running AddonV as administrator.)"
        ),

        # installer messages (ELS)
        "els_src_missing": "Source does not exist: {path}",
        "els_not_vcf": "'{name}' doesn't look like an ELS-VCF file.",
        "els_no_xmls": "No ELS-VCF XML files found.",
        "els_copy_failed": "Could not install ELS '{name}': {err}",
        "els_copy_failed_partial": "Stopped after {copied} file(s): could not copy '{name}': {err}",
        "els_summary": "ELS — {copied} file(s) installed, {skipped} kept.",

        # generic errors
        "drop_nothing": "Nothing usable was dropped (only files and folders are supported).",
        "unexpected_error": "Unexpected error: {err}",

        # replace confirmation
        "replace_title": "Replace?",
        "dlc_replace_body": "DLC '{name}' already exists.\n\nReplace the existing version?",
        "dlc_kept": "DLC '{name}' kept — not replaced.",
        "els_replace_body": "ELS '{name}' already exists in the target folder.\n\nReplace the existing file(s)?",
        "els_kept": "ELS '{name}' kept — not replaced.",

        # dlclist
        "dlclist_paths_close_missing": "`</Paths>` not found in dlclist.xml — file broken?",
    },

    "de": {
        "window_title": "AddonV",
        "ok": "OK",
        "cancel": "Abbrechen",
        "yes": "Ja",
        "no": "Nein",

        "lang_dialog_title": "Sprache wählen",
        "lang_dialog_hint": "Wähle deine bevorzugte Sprache:",
        "lang_button": "🌐 Sprache",

        "manage_btn": "📦 Mods verwalten",
        "manage_dialog_title": "Installierte DLC-Mods",
        "manage_empty": "Keine DLC-Mods installiert.",
        "manage_remove_btn": "Entfernen",
        "manage_disable_btn": "Deaktivieren",
        "manage_enable_btn": "Aktivieren",
        "manage_repair_btn": "dlclist reparieren",
        "manage_state_active": "aktiv",
        "manage_state_disabled": "deaktiviert",
        "manage_state_unlisted": "nicht in dlclist",
        "manage_state_duplicate": "doppelt",
        "manage_search_placeholder": "Mods suchen…",
        "manage_no_matches": "Keine Mods passen zur Suche.",
        "manage_sort_order": "Ladereihenfolge (dlclist)",
        "manage_close_btn": "Schließen",
        "manage_sort_label": "Sortieren nach:",
        "manage_sort_name": "Name (A–Z)",
        "manage_sort_date": "Hinzugefügt (neueste)",
        "manage_added": "hinzugefügt {date}",
        "manage_confirm_title": "Mod entfernen?",
        "manage_confirm_body": "DLC '{name}' entfernen?\n\nDer Pack-Ordner und sein dlclist.xml-Eintrag werden gelöscht.",
        "dlc_removing": "Entferne DLC '{name}'…",
        "dlc_removed": "DLC '{name}' entfernt.",
        "dlc_remove_failed": "DLC '{name}' konnte nicht entfernt werden: {err}",
        "dlc_not_installed": "DLC '{name}' ist nicht installiert.",
        "dlclist_entry_removed": "dlclist.xml: Eintrag für '{name}' entfernt.",
        "dlclist_disabled": "dlclist.xml: '{name}' deaktiviert (auskommentiert).",
        "dlclist_enabled": "dlclist.xml: '{name}' aktiviert.",
        "dlclist_duplicate": "dlclist.xml: '{name}' ist mehrfach eingetragen — Duplikat entfernen.",

        # repair dlclist
        "repair_none": "dlclist.xml: nichts zu reparieren — Liste passt zu den installierten Packs.",
        "repair_added": "dlclist.xml: fehlenden Eintrag für '{name}' wieder hinzugefügt.",
        "repair_removed": "dlclist.xml: Eintrag für fehlendes '{name}' entfernt.",
        "repair_missing_title": "Ordner fehlt",
        "repair_missing_body": (
            "'{name}' steht in der dlclist.xml, aber der Pack-Ordner fehlt.\n\n"
            "Eintrag aus der dlclist.xml entfernen?"
        ),
        "repair_summary": "Reparatur fertig: {added} hinzugefügt, {removed} entfernt, {kept} behalten.",

        "choose_gta_btn": "GTA-Pfad wählen…",
        "gta_path_label": "GTA-Pfad:  {path}",
        "gta_path_unset": "GTA-Pfad:  (nicht gesetzt — bitte wählen)",
        "mods_checkbox": "In /mods-Unterordner installieren (empfohlen, lässt Originaldateien unberührt)",
        "mode_safe": "Modus: sicher (mods/)",
        "mode_direct": "Modus: DIREKT — Originaldateien werden verändert!",

        "drop_zone_title": "Mods hier ablegen",
        "drop_zone_hint": (
            "DLC-Ordner (mit dlc.rpf) oder ELS-VCF .xml-Dateien/-Ordner hier hineinziehen.\n"
            "AddonV erkennt den Typ automatisch:\n"
            "DLC → mods/update/x64/dlcpacks (+ dlclist.xml) · ELS → ELS/pack_default."
        ),
        "drop_unknown": (
            "Konnte '{name}' nicht zuordnen — bitte einen DLC-Ordner "
            "(mit dlc.rpf) oder ELS-VCF .xml-Datei(en) ablegen."
        ),

        "dlclist_btn": "dlclist.xml wählen…",
        "dlclist_clear_btn": "zurücksetzen",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (optional — extrahierte Datei für automatische Bearbeitung)",

        "gta_detected": "GTA automatisch erkannt: {path}",
        "gta_not_detected": "Hinweis: GTA-Pfad nicht automatisch erkannt — bitte oben wählen.",
        "gta_path_set": "GTA-Pfad gesetzt: {path}",
        "dlclist_set": "dlclist.xml gesetzt: {path}",
        "direct_enabled": "Direktinstallation aktiviert — Originaldateien werden verändert.",
        "safe_enabled": "Sichere Installation aktiviert (mods/-Unterordner).",
        "dlclist_added": "dlclist.xml: Eintrag für '{name}' hinzugefügt.",
        "dlclist_existed": "dlclist.xml: Eintrag für '{name}' war bereits vorhanden.",
        "dlclist_error": "Fehler beim Bearbeiten von dlclist.xml: {err}",
        "dlclist_hint_no_xml": (
            "Hinweis: keine extrahierte dlclist.xml konfiguriert.\n"
            "  Bitte folgenden Eintrag in update.rpf/common/data/dlclist.xml\n"
            "  vor </Paths> einfügen (z. B. via OpenIV):\n{entry}"
        ),

        "gta_missing_title": "GTA-Pfad fehlt",
        "gta_missing_body": "Bitte zuerst den GTA-Installationspfad wählen.",
        "invalid_folder_title": "Ungültiger Ordner",
        "invalid_folder_body": "Dieser Ordner enthält keine GTA5.exe / GTAVLauncher.exe.",
        "choose_gta_dialog": "GTA-Installationsordner wählen",
        "choose_dlclist_dialog": "extrahierte dlclist.xml wählen",
        "direct_warning_title": "Direktinstallation – Achtung!",
        "direct_warning_body": (
            "Du bist dabei, Mods direkt in den GTA-Hauptordner zu installieren.\n\n"
            "Risiken:\n"
            "• Original-Spieldateien werden überschrieben.\n"
            "• Spiel-Updates oder Online-/Anti-Cheat-Prüfungen können fehlschlagen.\n"
            "• Fehlerhafte Mods können das Spiel unspielbar machen.\n"
            "• Ohne Backup ist ein Rollback nur per Neuinstallation möglich.\n\n"
            "Empfohlen wird der mods/-Unterordner (OpenIV-Konvention),\n"
            "der die Originaldateien unangetastet lässt.\n\n"
            "Trotzdem direkt in den GTA-Hauptordner installieren?"
        ),

        "dlc_exists": "DLC '{name}' existiert bereits.",
        "dlc_installing": "Installiere DLC '{name}'…",
        "dlc_installed": "DLC '{name}' installiert ({size}).",
        "dlc_copy_failed": (
            "DLC '{name}' konnte nicht installiert werden: {err}\n"
            "  (Tipp: Für die Installation in Program Files muss AddonV evtl. als Administrator laufen.)"
        ),

        "els_src_missing": "Quelle existiert nicht: {path}",
        "els_not_vcf": "'{name}' sieht nicht nach einer ELS-VCF-Datei aus.",
        "els_no_xmls": "Keine ELS-VCF-XML-Dateien gefunden.",
        "els_copy_failed": "ELS '{name}' konnte nicht installiert werden: {err}",
        "els_copy_failed_partial": "Nach {copied} Datei(en) abgebrochen: '{name}' konnte nicht kopiert werden: {err}",
        "els_summary": "ELS — {copied} Datei(en) installiert, {skipped} behalten.",

        "drop_nothing": "Nichts Verwertbares abgelegt (nur Dateien und Ordner werden unterstützt).",
        "unexpected_error": "Unerwarteter Fehler: {err}",

        "replace_title": "Ersetzen?",
        "dlc_replace_body": "DLC '{name}' existiert bereits.\n\nVorhandene Version ersetzen?",
        "dlc_kept": "DLC '{name}' beibehalten — nicht ersetzt.",
        "els_replace_body": "ELS '{name}' existiert bereits im Zielordner.\n\nVorhandene Datei(en) ersetzen?",
        "els_kept": "ELS '{name}' beibehalten — nicht ersetzt.",

        "dlclist_paths_close_missing": "`</Paths>` in dlclist.xml nicht gefunden — Datei kaputt?",
    },

    "ru": {
        "window_title": "AddonV",
        "ok": "OK",
        "cancel": "Отмена",
        "yes": "Да",
        "no": "Нет",

        "lang_dialog_title": "Выбор языка",
        "lang_dialog_hint": "Выберите предпочитаемый язык:",
        "lang_button": "🌐 Язык",

        "manage_btn": "📦 Управление модами",
        "manage_dialog_title": "Установленные DLC-моды",
        "manage_empty": "DLC-моды не установлены.",
        "manage_remove_btn": "Удалить",
        "manage_disable_btn": "Отключить",
        "manage_enable_btn": "Включить",
        "manage_repair_btn": "Исправить dlclist",
        "manage_state_active": "активен",
        "manage_state_disabled": "отключён",
        "manage_state_unlisted": "нет в dlclist",
        "manage_state_duplicate": "дубликат",
        "manage_search_placeholder": "Поиск модов…",
        "manage_no_matches": "Нет модов по запросу.",
        "manage_sort_order": "Порядок загрузки (dlclist)",
        "manage_close_btn": "Закрыть",
        "manage_sort_label": "Сортировка:",
        "manage_sort_name": "Имя (А–Я)",
        "manage_sort_date": "Дата добавления (новые)",
        "manage_added": "добавлено {date}",
        "manage_confirm_title": "Удалить мод?",
        "manage_confirm_body": "Удалить DLC '{name}'?\n\nПапка пака и его запись в dlclist.xml будут удалены.",
        "dlc_removing": "Удаляю DLC '{name}'…",
        "dlc_removed": "DLC '{name}' удалён.",
        "dlc_remove_failed": "Не удалось удалить DLC '{name}': {err}",
        "dlc_not_installed": "DLC '{name}' не установлен.",
        "dlclist_entry_removed": "dlclist.xml: запись для '{name}' удалена.",
        "dlclist_disabled": "dlclist.xml: '{name}' отключён (закомментирован).",
        "dlclist_enabled": "dlclist.xml: '{name}' включён.",
        "dlclist_duplicate": "dlclist.xml: '{name}' указан несколько раз — удалите дубликат.",

        # repair dlclist
        "repair_none": "dlclist.xml: исправлять нечего — список соответствует установленным пакам.",
        "repair_added": "dlclist.xml: восстановлена отсутствующая запись для '{name}'.",
        "repair_removed": "dlclist.xml: удалена запись для отсутствующего '{name}'.",
        "repair_missing_title": "Папка отсутствует",
        "repair_missing_body": (
            "'{name}' указан в dlclist.xml, но папка пака отсутствует.\n\n"
            "Удалить запись из dlclist.xml?"
        ),
        "repair_summary": "Готово: добавлено {added}, удалено {removed}, оставлено {kept}.",

        "choose_gta_btn": "Выбрать путь к GTA…",
        "gta_path_label": "Путь к GTA:  {path}",
        "gta_path_unset": "Путь к GTA:  (не задан — выберите)",
        "mods_checkbox": "Устанавливать в подпапку /mods (рекомендуется — оригинальные файлы не трогаются)",
        "mode_safe": "Режим: безопасный (mods/)",
        "mode_direct": "Режим: ПРЯМОЙ — оригинальные файлы будут изменены!",

        "drop_zone_title": "Перетащите моды сюда",
        "drop_zone_hint": (
            "Перетащите сюда папки DLC (с dlc.rpf) или ELS-VCF .xml-файлы/папки.\n"
            "AddonV определяет тип автоматически:\n"
            "DLC → mods/update/x64/dlcpacks (+ dlclist.xml) · ELS → ELS/pack_default."
        ),
        "drop_unknown": (
            "Не удалось определить, что такое '{name}' — перетащите папку DLC "
            "(с dlc.rpf) или ELS-VCF .xml-файл(ы)."
        ),

        "dlclist_btn": "Выбрать dlclist.xml…",
        "dlclist_clear_btn": "сбросить",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (необязательно — извлечённый файл для автоматической правки)",

        "gta_detected": "GTA найдена автоматически: {path}",
        "gta_not_detected": "Примечание: путь к GTA не определён автоматически — выберите выше.",
        "gta_path_set": "Путь к GTA задан: {path}",
        "dlclist_set": "dlclist.xml задан: {path}",
        "direct_enabled": "Прямая установка включена — оригинальные файлы будут изменены.",
        "safe_enabled": "Безопасная установка включена (подпапка mods/).",
        "dlclist_added": "dlclist.xml: запись для '{name}' добавлена.",
        "dlclist_existed": "dlclist.xml: запись для '{name}' уже существует.",
        "dlclist_error": "Ошибка при правке dlclist.xml: {err}",
        "dlclist_hint_no_xml": (
            "Примечание: извлечённый dlclist.xml не настроен.\n"
            "  Пожалуйста, добавьте следующую запись в update.rpf/common/data/dlclist.xml\n"
            "  перед </Paths> (например, через OpenIV):\n{entry}"
        ),

        "gta_missing_title": "Путь к GTA не задан",
        "gta_missing_body": "Сначала выберите путь установки GTA.",
        "invalid_folder_title": "Недопустимая папка",
        "invalid_folder_body": "В этой папке нет GTA5.exe / GTAVLauncher.exe.",
        "choose_gta_dialog": "Выберите папку установки GTA",
        "choose_dlclist_dialog": "Выберите извлечённый dlclist.xml",
        "direct_warning_title": "Прямая установка – внимание!",
        "direct_warning_body": (
            "Вы собираетесь установить моды прямо в основную папку GTA.\n\n"
            "Риски:\n"
            "• Оригинальные файлы игры будут перезаписаны.\n"
            "• Обновления игры или проверки онлайн/анти-чита могут не пройти.\n"
            "• Неисправные моды могут сделать игру неиграбельной.\n"
            "• Без резервной копии откат возможен только переустановкой.\n\n"
            "Рекомендуется подпапка mods/ (соглашение OpenIV),\n"
            "она оставляет оригинальные файлы нетронутыми.\n\n"
            "Всё равно установить прямо в основную папку GTA?"
        ),

        "dlc_exists": "DLC '{name}' уже существует.",
        "dlc_installing": "Устанавливаю DLC '{name}'…",
        "dlc_installed": "DLC '{name}' установлен ({size}).",
        "dlc_copy_failed": (
            "Не удалось установить DLC '{name}': {err}\n"
            "  (Совет: для установки в Program Files может потребоваться запуск AddonV от имени администратора.)"
        ),

        "els_src_missing": "Источник не существует: {path}",
        "els_not_vcf": "'{name}' не похож на ELS-VCF файл.",
        "els_no_xmls": "ELS-VCF XML-файлы не найдены.",
        "els_copy_failed": "Не удалось установить ELS '{name}': {err}",
        "els_copy_failed_partial": "Остановлено после {copied} файл(ов): не удалось скопировать '{name}': {err}",
        "els_summary": "ELS — установлено файлов: {copied}, сохранено: {skipped}.",

        "drop_nothing": "Не перетащено ничего подходящего (поддерживаются только файлы и папки).",
        "unexpected_error": "Непредвиденная ошибка: {err}",

        "replace_title": "Заменить?",
        "dlc_replace_body": "DLC '{name}' уже существует.\n\nЗаменить существующую версию?",
        "dlc_kept": "DLC '{name}' сохранён — не заменён.",
        "els_replace_body": "ELS '{name}' уже существует в целевой папке.\n\nЗаменить существующий файл(ы)?",
        "els_kept": "ELS '{name}' сохранён — не заменён.",

        "dlclist_paths_close_missing": "`</Paths>` не найден в dlclist.xml — файл повреждён?",
    },

    "es": {
        "window_title": "AddonV",
        "ok": "OK",
        "cancel": "Cancelar",
        "yes": "Sí",
        "no": "No",

        "lang_dialog_title": "Elegir idioma",
        "lang_dialog_hint": "Selecciona tu idioma preferido:",
        "lang_button": "🌐 Idioma",

        "manage_btn": "📦 Gestionar mods",
        "manage_dialog_title": "Mods DLC instalados",
        "manage_empty": "No hay mods DLC instalados.",
        "manage_remove_btn": "Eliminar",
        "manage_disable_btn": "Desactivar",
        "manage_enable_btn": "Activar",
        "manage_repair_btn": "Reparar dlclist",
        "manage_state_active": "activo",
        "manage_state_disabled": "desactivado",
        "manage_state_unlisted": "no en dlclist",
        "manage_state_duplicate": "duplicado",
        "manage_search_placeholder": "Buscar mods…",
        "manage_no_matches": "Ningún mod coincide con la búsqueda.",
        "manage_sort_order": "Orden de carga (dlclist)",
        "manage_close_btn": "Cerrar",
        "manage_sort_label": "Ordenar por:",
        "manage_sort_name": "Nombre (A–Z)",
        "manage_sort_date": "Fecha de adición (recientes)",
        "manage_added": "añadido {date}",
        "manage_confirm_title": "¿Eliminar mod?",
        "manage_confirm_body": "¿Eliminar el DLC '{name}'?\n\nLa carpeta del pack y su entrada en dlclist.xml se eliminarán.",
        "dlc_removing": "Eliminando DLC '{name}'…",
        "dlc_removed": "DLC '{name}' eliminado.",
        "dlc_remove_failed": "No se pudo eliminar el DLC '{name}': {err}",
        "dlc_not_installed": "El DLC '{name}' no está instalado.",
        "dlclist_entry_removed": "dlclist.xml: entrada para '{name}' eliminada.",
        "dlclist_disabled": "dlclist.xml: '{name}' desactivado (comentado).",
        "dlclist_enabled": "dlclist.xml: '{name}' activado.",
        "dlclist_duplicate": "dlclist.xml: '{name}' aparece más de una vez — elimina el duplicado.",

        # repair dlclist
        "repair_none": "dlclist.xml: nada que reparar — la lista coincide con los packs instalados.",
        "repair_added": "dlclist.xml: entrada para '{name}' restaurada.",
        "repair_removed": "dlclist.xml: entrada del '{name}' faltante eliminada.",
        "repair_missing_title": "Falta la carpeta",
        "repair_missing_body": (
            "'{name}' aparece en dlclist.xml pero falta su carpeta de pack.\n\n"
            "¿Eliminar la entrada de dlclist.xml?"
        ),
        "repair_summary": "Reparación lista: {added} añadidas, {removed} eliminadas, {kept} conservadas.",

        "choose_gta_btn": "Elegir ruta de GTA…",
        "gta_path_label": "Ruta de GTA:  {path}",
        "gta_path_unset": "Ruta de GTA:  (no establecida — elige una)",
        "mods_checkbox": "Instalar en la subcarpeta /mods (recomendado — no toca los archivos originales)",
        "mode_safe": "Modo: seguro (mods/)",
        "mode_direct": "Modo: DIRECTO — ¡los archivos originales serán modificados!",

        "drop_zone_title": "Suelta los mods aquí",
        "drop_zone_hint": (
            "Arrastra aquí carpetas DLC (con dlc.rpf) o archivos/carpetas ELS-VCF .xml.\n"
            "AddonV detecta el tipo automáticamente:\n"
            "DLC → mods/update/x64/dlcpacks (+ dlclist.xml) · ELS → ELS/pack_default."
        ),
        "drop_unknown": (
            "No se pudo identificar '{name}' — arrastra una carpeta DLC "
            "(con dlc.rpf) o archivo(s) ELS-VCF .xml."
        ),

        "dlclist_btn": "Elegir dlclist.xml…",
        "dlclist_clear_btn": "restablecer",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (opcional — archivo extraído para edición automática)",

        "gta_detected": "GTA detectado automáticamente: {path}",
        "gta_not_detected": "Aviso: la ruta de GTA no se detectó automáticamente — elige arriba.",
        "gta_path_set": "Ruta de GTA establecida: {path}",
        "dlclist_set": "dlclist.xml establecido: {path}",
        "direct_enabled": "Instalación directa activada — los archivos originales serán modificados.",
        "safe_enabled": "Instalación segura activada (subcarpeta mods/).",
        "dlclist_added": "dlclist.xml: entrada para '{name}' añadida.",
        "dlclist_existed": "dlclist.xml: la entrada para '{name}' ya existía.",
        "dlclist_error": "Error al editar dlclist.xml: {err}",
        "dlclist_hint_no_xml": (
            "Aviso: no hay dlclist.xml extraído configurado.\n"
            "  Añade la siguiente entrada en update.rpf/common/data/dlclist.xml\n"
            "  antes de </Paths> (p. ej. con OpenIV):\n{entry}"
        ),

        "gta_missing_title": "Falta la ruta de GTA",
        "gta_missing_body": "Por favor, elige primero la ruta de instalación de GTA.",
        "invalid_folder_title": "Carpeta inválida",
        "invalid_folder_body": "Esta carpeta no contiene GTA5.exe / GTAVLauncher.exe.",
        "choose_gta_dialog": "Elegir carpeta de instalación de GTA",
        "choose_dlclist_dialog": "Elegir dlclist.xml extraído",
        "direct_warning_title": "Instalación directa – ¡Atención!",
        "direct_warning_body": (
            "Estás a punto de instalar mods directamente en la carpeta principal de GTA.\n\n"
            "Riesgos:\n"
            "• Los archivos originales del juego serán sobrescritos.\n"
            "• Las actualizaciones del juego o las comprobaciones online/anti-cheat pueden fallar.\n"
            "• Mods defectuosos pueden hacer el juego injugable.\n"
            "• Sin copia de seguridad, solo se puede revertir reinstalando.\n\n"
            "Se recomienda la subcarpeta mods/ (convención de OpenIV),\n"
            "que deja los archivos originales intactos.\n\n"
            "¿Instalar de todas formas directamente en la carpeta principal de GTA?"
        ),

        "dlc_exists": "El DLC '{name}' ya existe.",
        "dlc_installing": "Instalando DLC '{name}'…",
        "dlc_installed": "DLC '{name}' instalado ({size}).",
        "dlc_copy_failed": (
            "No se pudo instalar el DLC '{name}': {err}\n"
            "  (Consejo: instalar en Program Files puede requerir ejecutar AddonV como administrador.)"
        ),

        "els_src_missing": "La fuente no existe: {path}",
        "els_not_vcf": "'{name}' no parece un archivo ELS-VCF.",
        "els_no_xmls": "No se encontraron archivos XML ELS-VCF.",
        "els_copy_failed": "No se pudo instalar ELS '{name}': {err}",
        "els_copy_failed_partial": "Detenido tras {copied} archivo(s): no se pudo copiar '{name}': {err}",
        "els_summary": "ELS — {copied} archivo(s) instalados, {skipped} conservados.",

        "drop_nothing": "No se soltó nada utilizable (solo se admiten archivos y carpetas).",
        "unexpected_error": "Error inesperado: {err}",

        "replace_title": "¿Reemplazar?",
        "dlc_replace_body": "El DLC '{name}' ya existe.\n\n¿Reemplazar la versión existente?",
        "dlc_kept": "DLC '{name}' conservado — no reemplazado.",
        "els_replace_body": "ELS '{name}' ya existe en la carpeta de destino.\n\n¿Reemplazar el/los archivo(s) existente(s)?",
        "els_kept": "ELS '{name}' conservado — no reemplazado.",

        "dlclist_paths_close_missing": "`</Paths>` no encontrado en dlclist.xml — ¿archivo dañado?",
    },
}
