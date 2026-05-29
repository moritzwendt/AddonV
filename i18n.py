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
        "manage_close_btn": "Close",
        "manage_confirm_title": "Remove mod?",
        "manage_confirm_body": "Remove DLC '{name}'?\n\nThe pack folder and its dlclist.xml entry will be deleted.",
        "dlc_removing": "Removing DLC '{name}'…",
        "dlc_removed": "DLC '{name}' removed.",
        "dlc_remove_failed": "Could not remove DLC '{name}': {err}",
        "dlc_not_installed": "DLC '{name}' is not installed.",
        "dlclist_entry_removed": "dlclist.xml: entry for '{name}' removed.",

        # path / mode
        "choose_gta_btn": "Choose GTA path…",
        "gta_path_label": "GTA path:  {path}",
        "gta_path_unset": "GTA path:  (not set — please choose)",
        "mods_checkbox": "Install into /mods subfolder (recommended — keeps original files untouched)",
        "mode_safe": "Mode: safe (mods/)",
        "mode_direct": "Mode: DIRECT — original files will be modified!",

        # drop zones
        "dlc_zone_title": "DLC Mods",
        "dlc_zone_hint": (
            "Drag a folder containing dlc.rpf here.\n"
            "Will be copied to mods/update/x64/dlcpacks\n"
            "and registered in dlclist.xml."
        ),
        "els_zone_title": "ELS Mods",
        "els_zone_hint": (
            "Drag ELS-VCF .xml files or folders here.\n"
            "Will be copied to ELS/pack_default."
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
        "direct_enabled": "[!!] Direct installation enabled — original files will be modified.",
        "safe_enabled": "[OK] Safe installation enabled (mods/ subfolder).",
        "dlclist_added": "[OK] dlclist.xml: entry for '{name}' added.",
        "dlclist_existed": "[OK] dlclist.xml: entry for '{name}' already present.",
        "dlclist_error": "[!!] Error editing dlclist.xml: {err}",
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
        "dlc_no_rpf": "No 'dlc.rpf' found in '{name}' — likely not a DLC mod.",
        "dlc_exists": "DLC '{name}' already exists in {dir}.",
        "dlc_copying": "Copying DLC '{name}' to {dir}…",
        "dlc_installed": "DLC '{name}' installed.",
        "dlc_copy_failed": (
            "Could not install DLC '{name}': {err}\n"
            "  (Tip: installing into Program Files may require running AddonV as administrator.)"
        ),

        # installer messages (ELS)
        "els_src_missing": "Source does not exist: {path}",
        "els_not_vcf": "'{name}' doesn't look like an ELS-VCF file.",
        "els_file_exists": "File already exists: {name}",
        "els_copying_file": "Copying ELS file '{name}'…",
        "els_installed_file": "ELS file '{name}' installed.",
        "els_no_xmls": "No ELS-VCF XML files found.",
        "els_some_exist": "{count} ELS file(s) already exist in the target folder.",
        "els_copy_failed": "Could not install ELS '{name}': {err}",
        "els_copy_failed_partial": "Stopped after {copied} file(s): could not copy '{name}': {err}",
        "els_skipped": "  skipped (exists): {name}",
        "els_copying": "  copying {name}",
        "els_summary": "ELS: {copied} copied, {skipped} skipped.",

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
        "manage_close_btn": "Schließen",
        "manage_confirm_title": "Mod entfernen?",
        "manage_confirm_body": "DLC '{name}' entfernen?\n\nDer Pack-Ordner und sein dlclist.xml-Eintrag werden gelöscht.",
        "dlc_removing": "Entferne DLC '{name}'…",
        "dlc_removed": "DLC '{name}' entfernt.",
        "dlc_remove_failed": "DLC '{name}' konnte nicht entfernt werden: {err}",
        "dlc_not_installed": "DLC '{name}' ist nicht installiert.",
        "dlclist_entry_removed": "dlclist.xml: Eintrag für '{name}' entfernt.",

        "choose_gta_btn": "GTA-Pfad wählen…",
        "gta_path_label": "GTA-Pfad:  {path}",
        "gta_path_unset": "GTA-Pfad:  (nicht gesetzt — bitte wählen)",
        "mods_checkbox": "In /mods-Unterordner installieren (empfohlen, lässt Originaldateien unberührt)",
        "mode_safe": "Modus: sicher (mods/)",
        "mode_direct": "Modus: DIREKT — Originaldateien werden verändert!",

        "dlc_zone_title": "DLC Mods",
        "dlc_zone_hint": (
            "Ordner mit dlc.rpf hier hineinziehen.\n"
            "Wird nach mods/update/x64/dlcpacks kopiert\n"
            "und in dlclist.xml eingetragen."
        ),
        "els_zone_title": "ELS Mods",
        "els_zone_hint": (
            "ELS-VCF .xml-Dateien oder -Ordner hier hineinziehen.\n"
            "Wird nach ELS/pack_default kopiert."
        ),

        "dlclist_btn": "dlclist.xml wählen…",
        "dlclist_clear_btn": "zurücksetzen",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (optional — extrahierte Datei für automatische Bearbeitung)",

        "gta_detected": "GTA automatisch erkannt: {path}",
        "gta_not_detected": "Hinweis: GTA-Pfad nicht automatisch erkannt — bitte oben wählen.",
        "gta_path_set": "GTA-Pfad gesetzt: {path}",
        "dlclist_set": "dlclist.xml gesetzt: {path}",
        "direct_enabled": "[!!] Direktinstallation aktiviert — Originaldateien werden verändert.",
        "safe_enabled": "[OK] Sichere Installation aktiviert (mods/-Unterordner).",
        "dlclist_added": "[OK] dlclist.xml: Eintrag für '{name}' hinzugefügt.",
        "dlclist_existed": "[OK] dlclist.xml: Eintrag für '{name}' war bereits vorhanden.",
        "dlclist_error": "[!!] Fehler beim Bearbeiten von dlclist.xml: {err}",
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

        "dlc_no_rpf": "Kein 'dlc.rpf' in '{name}' gefunden — vermutlich keine DLC-Mod.",
        "dlc_exists": "DLC '{name}' existiert bereits unter {dir}.",
        "dlc_copying": "Kopiere DLC '{name}' nach {dir}…",
        "dlc_installed": "DLC '{name}' installiert.",
        "dlc_copy_failed": (
            "DLC '{name}' konnte nicht installiert werden: {err}\n"
            "  (Tipp: Für die Installation in Program Files muss AddonV evtl. als Administrator laufen.)"
        ),

        "els_src_missing": "Quelle existiert nicht: {path}",
        "els_not_vcf": "'{name}' sieht nicht nach einer ELS-VCF-Datei aus.",
        "els_file_exists": "Datei existiert bereits: {name}",
        "els_copying_file": "Kopiere ELS-Datei '{name}'…",
        "els_installed_file": "ELS-Datei '{name}' installiert.",
        "els_no_xmls": "Keine ELS-VCF-XML-Dateien gefunden.",
        "els_some_exist": "{count} ELS-Datei(en) existieren bereits im Zielordner.",
        "els_copy_failed": "ELS '{name}' konnte nicht installiert werden: {err}",
        "els_copy_failed_partial": "Nach {copied} Datei(en) abgebrochen: '{name}' konnte nicht kopiert werden: {err}",
        "els_skipped": "  übersprungen (existiert): {name}",
        "els_copying": "  kopiere {name}",
        "els_summary": "ELS: {copied} kopiert, {skipped} übersprungen.",

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
        "manage_close_btn": "Закрыть",
        "manage_confirm_title": "Удалить мод?",
        "manage_confirm_body": "Удалить DLC '{name}'?\n\nПапка пака и его запись в dlclist.xml будут удалены.",
        "dlc_removing": "Удаляю DLC '{name}'…",
        "dlc_removed": "DLC '{name}' удалён.",
        "dlc_remove_failed": "Не удалось удалить DLC '{name}': {err}",
        "dlc_not_installed": "DLC '{name}' не установлен.",
        "dlclist_entry_removed": "dlclist.xml: запись для '{name}' удалена.",

        "choose_gta_btn": "Выбрать путь к GTA…",
        "gta_path_label": "Путь к GTA:  {path}",
        "gta_path_unset": "Путь к GTA:  (не задан — выберите)",
        "mods_checkbox": "Устанавливать в подпапку /mods (рекомендуется — оригинальные файлы не трогаются)",
        "mode_safe": "Режим: безопасный (mods/)",
        "mode_direct": "Режим: ПРЯМОЙ — оригинальные файлы будут изменены!",

        "dlc_zone_title": "DLC моды",
        "dlc_zone_hint": (
            "Перетащите сюда папку с dlc.rpf.\n"
            "Будет скопирована в mods/update/x64/dlcpacks\n"
            "и добавлена в dlclist.xml."
        ),
        "els_zone_title": "ELS моды",
        "els_zone_hint": (
            "Перетащите сюда ELS-VCF .xml-файлы или папки.\n"
            "Будут скопированы в ELS/pack_default."
        ),

        "dlclist_btn": "Выбрать dlclist.xml…",
        "dlclist_clear_btn": "сбросить",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (необязательно — извлечённый файл для автоматической правки)",

        "gta_detected": "GTA найдена автоматически: {path}",
        "gta_not_detected": "Примечание: путь к GTA не определён автоматически — выберите выше.",
        "gta_path_set": "Путь к GTA задан: {path}",
        "dlclist_set": "dlclist.xml задан: {path}",
        "direct_enabled": "[!!] Прямая установка включена — оригинальные файлы будут изменены.",
        "safe_enabled": "[OK] Безопасная установка включена (подпапка mods/).",
        "dlclist_added": "[OK] dlclist.xml: запись для '{name}' добавлена.",
        "dlclist_existed": "[OK] dlclist.xml: запись для '{name}' уже существует.",
        "dlclist_error": "[!!] Ошибка при правке dlclist.xml: {err}",
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

        "dlc_no_rpf": "В '{name}' не найден 'dlc.rpf' — вероятно, это не DLC-мод.",
        "dlc_exists": "DLC '{name}' уже существует в {dir}.",
        "dlc_copying": "Копирую DLC '{name}' в {dir}…",
        "dlc_installed": "DLC '{name}' установлен.",
        "dlc_copy_failed": (
            "Не удалось установить DLC '{name}': {err}\n"
            "  (Совет: для установки в Program Files может потребоваться запуск AddonV от имени администратора.)"
        ),

        "els_src_missing": "Источник не существует: {path}",
        "els_not_vcf": "'{name}' не похож на ELS-VCF файл.",
        "els_file_exists": "Файл уже существует: {name}",
        "els_copying_file": "Копирую ELS-файл '{name}'…",
        "els_installed_file": "ELS-файл '{name}' установлен.",
        "els_no_xmls": "ELS-VCF XML-файлы не найдены.",
        "els_some_exist": "{count} ELS-файл(ов) уже существуют в целевой папке.",
        "els_copy_failed": "Не удалось установить ELS '{name}': {err}",
        "els_copy_failed_partial": "Остановлено после {copied} файл(ов): не удалось скопировать '{name}': {err}",
        "els_skipped": "  пропущен (существует): {name}",
        "els_copying": "  копирую {name}",
        "els_summary": "ELS: {copied} скопировано, {skipped} пропущено.",

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
        "manage_close_btn": "Cerrar",
        "manage_confirm_title": "¿Eliminar mod?",
        "manage_confirm_body": "¿Eliminar el DLC '{name}'?\n\nLa carpeta del pack y su entrada en dlclist.xml se eliminarán.",
        "dlc_removing": "Eliminando DLC '{name}'…",
        "dlc_removed": "DLC '{name}' eliminado.",
        "dlc_remove_failed": "No se pudo eliminar el DLC '{name}': {err}",
        "dlc_not_installed": "El DLC '{name}' no está instalado.",
        "dlclist_entry_removed": "dlclist.xml: entrada para '{name}' eliminada.",

        "choose_gta_btn": "Elegir ruta de GTA…",
        "gta_path_label": "Ruta de GTA:  {path}",
        "gta_path_unset": "Ruta de GTA:  (no establecida — elige una)",
        "mods_checkbox": "Instalar en la subcarpeta /mods (recomendado — no toca los archivos originales)",
        "mode_safe": "Modo: seguro (mods/)",
        "mode_direct": "Modo: DIRECTO — ¡los archivos originales serán modificados!",

        "dlc_zone_title": "Mods DLC",
        "dlc_zone_hint": (
            "Arrastra aquí una carpeta con dlc.rpf.\n"
            "Se copiará a mods/update/x64/dlcpacks\n"
            "y se registrará en dlclist.xml."
        ),
        "els_zone_title": "Mods ELS",
        "els_zone_hint": (
            "Arrastra aquí archivos ELS-VCF .xml o carpetas.\n"
            "Se copiarán a ELS/pack_default."
        ),

        "dlclist_btn": "Elegir dlclist.xml…",
        "dlclist_clear_btn": "restablecer",
        "dlclist_label": "dlclist.xml:  {path}",
        "dlclist_unset": "dlclist.xml:  (opcional — archivo extraído para edición automática)",

        "gta_detected": "GTA detectado automáticamente: {path}",
        "gta_not_detected": "Aviso: la ruta de GTA no se detectó automáticamente — elige arriba.",
        "gta_path_set": "Ruta de GTA establecida: {path}",
        "dlclist_set": "dlclist.xml establecido: {path}",
        "direct_enabled": "[!!] Instalación directa activada — los archivos originales serán modificados.",
        "safe_enabled": "[OK] Instalación segura activada (subcarpeta mods/).",
        "dlclist_added": "[OK] dlclist.xml: entrada para '{name}' añadida.",
        "dlclist_existed": "[OK] dlclist.xml: la entrada para '{name}' ya existía.",
        "dlclist_error": "[!!] Error al editar dlclist.xml: {err}",
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

        "dlc_no_rpf": "No se encontró 'dlc.rpf' en '{name}' — probablemente no es un mod DLC.",
        "dlc_exists": "El DLC '{name}' ya existe en {dir}.",
        "dlc_copying": "Copiando DLC '{name}' a {dir}…",
        "dlc_installed": "DLC '{name}' instalado.",
        "dlc_copy_failed": (
            "No se pudo instalar el DLC '{name}': {err}\n"
            "  (Consejo: instalar en Program Files puede requerir ejecutar AddonV como administrador.)"
        ),

        "els_src_missing": "La fuente no existe: {path}",
        "els_not_vcf": "'{name}' no parece un archivo ELS-VCF.",
        "els_file_exists": "El archivo ya existe: {name}",
        "els_copying_file": "Copiando archivo ELS '{name}'…",
        "els_installed_file": "Archivo ELS '{name}' instalado.",
        "els_no_xmls": "No se encontraron archivos XML ELS-VCF.",
        "els_some_exist": "{count} archivo(s) ELS ya existen en la carpeta de destino.",
        "els_copy_failed": "No se pudo instalar ELS '{name}': {err}",
        "els_copy_failed_partial": "Detenido tras {copied} archivo(s): no se pudo copiar '{name}': {err}",
        "els_skipped": "  omitido (existe): {name}",
        "els_copying": "  copiando {name}",
        "els_summary": "ELS: {copied} copiados, {skipped} omitidos.",

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
