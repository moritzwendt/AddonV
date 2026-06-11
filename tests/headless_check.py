"""Headless verification for the file-renamer tab.

Isolates the user config (USERPROFILE/HOME -> tempdir) BEFORE importing config/
backend, loads qml/Main.qml offscreen, checks for QML errors, exercises the
renamer backend slots end-to-end and grabs a screenshot of the new page.

Run with:  py -3 tests\\headless_check.py
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# --- sandbox the config BEFORE anything reads Path.home() ---
sandbox = Path(tempfile.mkdtemp(prefix="addonv-test-"))
os.environ["USERPROFILE"] = str(sandbox)
os.environ["HOME"] = str(sandbox)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QUICK_BACKEND"] = "software"

# seed a config so the first-run language prompt / update check don't fire
cfg_dir = sandbox / ".addonv"
cfg_dir.mkdir(parents=True)
(cfg_dir / "config.json").write_text(json.dumps({
    "language": "de", "auto_check_updates": False, "save_terminal_history": False,
}), encoding="utf-8")

from PySide6.QtCore import Q_ARG, QMetaObject, QObject, Qt, QTimer, QUrl  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtQml import QQmlApplicationEngine  # noqa: E402

app = QApplication([])

import config  # noqa: E402
import backend as backend_mod  # noqa: E402
importlib.reload(config)
importlib.reload(backend_mod)
assert str(config.CONFIG_FILE).startswith(str(sandbox)), "config not sandboxed!"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        failures.append(name)


b = backend_mod.Backend()

# auto-answer any in-app dialog with its primary (last) button so nested event
# loops never hang headlessly (answer must come via QTimer, never inline).
# Answer THROUGH the QML overlay (dlg.resolve) — resolving via backend.resolveDialog
# directly would leave the full-window scrim visible, swallowing later hover events.
def _auto_answer(spec):
    btns = spec.get("buttons") or []
    choice = btns[-1]["id"] if btns else (spec.get("selected") or "")

    def answer():
        dlg = engine.rootObjects()[0].findChild(QObject, "dlg") if engine.rootObjects() else None
        if dlg is None or not QMetaObject.invokeMethod(
                dlg, "resolve", Qt.DirectConnection, Q_ARG("QVariant", choice)):
            b.resolveDialog(choice)   # fallback: at least unblock the nested loop

    QTimer.singleShot(0, answer)

b.dialogRequested.connect(_auto_answer)

# ---------- 1) QML loads without errors ----------
qml_warnings: list[str] = []
engine = QQmlApplicationEngine()
engine.warnings.connect(lambda errs: qml_warnings.extend(e.toString() for e in errs))
engine.rootContext().setContextProperty("backend", b)
engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
check("qml loads (root objects)", bool(engine.rootObjects()))

# pump a little so deferred bindings/Loaders settle
end = time.time() + 0.8
while time.time() < end:
    app.processEvents()
    time.sleep(0.01)
check("no qml warnings", not qml_warnings, "; ".join(qml_warnings[:5]))

win = engine.rootObjects()[0] if engine.rootObjects() else None

# ---------- 2) renamer flow: drop (models + XML mixed) -> detect -> execute ----------
check("no default destination", b.property("renameDest") == "")
check("rename state ready", b.property("renameState") == "ready")

src_dir = sandbox / "mod"
src_dir.mkdir()
set_names = ("FBI.ytd", "FBI.yft", "FBI_hi.yft", "FBI+hi.ytd", "FBI.xml", "FBI_hi.xml")
for n in set_names + ("carcols.xml", "readme.txt"):
    (src_dir / n).write_bytes(b"data-" + n.encode())

b.renameDrop([str(src_dir)])
check("base detected = fbi", b.property("renameBase") == "fbi")
files = b.property("renameFiles")
check("6 set files exposed (incl. xml)", len(files) == 6)
check("2 files skipped (carcols.xml, readme.txt)", b.property("renameSkipped") == 2)
groups = b.property("renameGroups")
check("fbi group leads (6 files)",
      len(groups) == 2 and groups[0]["base"] == "fbi" and groups[0]["count"] == 6)

dest = sandbox / "out"
dest.mkdir()
b.config.rename_last_dest = str(dest)
b.renameExecute("police2")
expected = {"police2.ytd", "police2.yft", "police2_hi.yft", "police2+hi.ytd",
            "police2.xml", "police2_hi.xml"}
got = {f.name for f in dest.iterdir()}
check("renamed copies written (incl. xml)", got == expected, f"got {sorted(got)}")
check("originals untouched", (src_dir / "FBI.ytd").is_file() and len(list(src_dir.iterdir())) == 8)
check("content copied", (dest / "police2_hi.xml").read_bytes() == b"data-FBI_hi.xml")
check("rename state done", b.property("renameState") == "done")
check("rename summary set", "6" in b.property("renameSummary"))

# overwrite prompt: run again — auto-answer presses the primary ("yes to all")
(dest / "police2.ytd").write_bytes(b"old")
b.renameExecute("police2")
check("overwrite via dialog", (dest / "police2.ytd").read_bytes() == b"data-FBI.ytd")

# multiple sets -> most common wins, selection switches
extra = sandbox / "police.ytd"
extra.write_bytes(b"x")
b.renameDrop([str(src_dir), str(extra)])
check("multi groups detected", len(b.property("renameGroups")) == 3)
check("most common selected", b.property("renameBase") == "fbi")
b.renameSelectBase("police")
check("base switchable", b.property("renameBase") == "police" and len(b.property("renameFiles")) == 1)
b.renameClear()
check("clear resets", b.property("renameBase") == "" and len(b.property("renameFiles")) == 0)

# ---------- 3) presets: defaults seeded, CRUD + persistence ----------
presets = b.property("renamePresets")
check("13 default presets", len(presets) == 13)
by_name = {p["name"]: p["model"] for p in presets}
check("default mapping ok", by_name.get("Polizei 2") == "police2" and by_name.get("Ranger") == "pranger")

b.saveRenamePreset({"id": "", "name": "Taxi Test", "model": "Taxi!"})
presets = b.property("renamePresets")
mine = next((p for p in presets if p["name"] == "Taxi Test"), None)
check("preset added + model sanitized", mine is not None and mine["model"] == "taxi")

# edit
b.saveRenamePreset({"id": mine["id"], "name": "Taxi Test 2", "model": "taxi2"})
presets = b.property("renamePresets")
check("preset edited", any(p["name"] == "Taxi Test 2" and p["model"] == "taxi2" for p in presets))

# persistence: a fresh Config.load() must still contain it (survives restart)
fresh = config.Config.load()
check("preset persisted to config.json",
      any(p.get("name") == "Taxi Test 2" for p in fresh.rename_presets))

# remove
b.removeRenamePreset(mine["id"])
presets = b.property("renamePresets")
check("preset removed", not any(p["id"] == mine["id"] for p in presets) and len(presets) == 13)

# ---------- 3b) drop zones: layout-preset save / edit / remove ----------
# mirror the UI flow: shrink the default auto zone, add a quarter zone, grow it
b.saveZone({"id": "auto", "name": "Auto", "auto": True, "rel": "", "color": "",
            "col": 0, "row": 0, "w": 2, "h": 1})
zones = b.property("dropZones")
check("auto zone shrunk to top half",
      len(zones) == 1 and zones[0]["w"] == 2 and zones[0]["h"] == 1)
b.saveZone({"id": "", "name": "Scripts", "auto": False, "rel": "scripts", "color": "",
            "col": 0, "row": 1, "w": 1, "h": 1})
zb = next((z for z in b.property("dropZones") if z["name"] == "Scripts"), None)
check("custom zone added (bottom-left quarter)",
      zb is not None and zb["col"] == 0 and zb["row"] == 1 and zb["w"] == 1 and zb["h"] == 1)
b.saveZone({"id": zb["id"], "name": "Scripts", "auto": False, "rel": "scripts", "color": "",
            "col": 0, "row": 1, "w": 2, "h": 1})
zb2 = next((z for z in b.property("dropZones") if z["id"] == zb["id"]), None)
check("zone edited to bottom half", zb2 is not None and zb2["w"] == 2 and zb2["h"] == 1)
check("zones persisted", len(config.Config.load().drop_zones) == 2)
b.removeZone(zb["id"])
check("zone removed", all(z["id"] != zb["id"] for z in b.property("dropZones")))
b.resetZones()

# ---------- 3c) profile accent colour ----------
b.saveProfile("Grid Test", ["packA"], [], "#5b8af0", "")
gp = next((p for p in b.property("profiles") if p["name"] == "Grid Test"), None)
check("profile colour saved", gp is not None and gp["color"] == "#5b8af0")
check("profile colour persisted",
      any(p.get("color") == "#5b8af0" for p in config.Config.load().profiles))
b.deleteProfile(gp["id"])   # confirm dialog → auto-answered through the QML overlay
check("profile deleted", all(p["id"] != gp["id"] for p in b.property("profiles")))

# ---------- 4) ELS routing for renamed XMLs ----------
check("xml-to-els setting default on", b.property("renameXmlToEls") is True)

ELS_XML = b"<vcfroot><sirens></sirens></vcfroot>"   # carries the '<vcf'/'<sirens' markers
gta = sandbox / "gta"
gta.mkdir()
(gta / "GTA5.exe").write_bytes(b"")
b.config.gta_path = str(gta)
b.renameChanged.emit()
els_target = gta / "ELS" / "pack_default"

# xml-only drop -> destination folder not needed, copy lands in the ELS folder
xml_dir = sandbox / "xmlonly"
xml_dir.mkdir()
(xml_dir / "FBI.xml").write_bytes(ELS_XML)
b.config.rename_last_dest = ""
b.renameDrop([str(xml_dir)])
check("xml-only: dest not needed", b.property("renameNeedsDest") is False)
b.renameExecute("police2")
check("xml-only -> ELS folder", (els_target / "police2.xml").is_file())
check("els summary variant", "ELS" in b.property("renameSummary"))

# mixed drop: model -> dest, ELS xml -> ELS folder, non-ELS xml -> dest
mix = sandbox / "mix"
mix.mkdir()
(mix / "SHERIFF.yft").write_bytes(b"m1")
(mix / "SHERIFF.xml").write_bytes(ELS_XML)
(mix / "SHERIFF_hi.xml").write_bytes(b"<plainxml></plainxml>")
b.renameDrop([str(mix)])
check("mixed: dest needed", b.property("renameNeedsDest") is True)
dest2 = sandbox / "out2"
dest2.mkdir()
b.config.rename_last_dest = str(dest2)
b.renameExecute("police3")
check("mixed: model -> dest", (dest2 / "police3.yft").is_file())
check("mixed: els xml -> ELS", (els_target / "police3.xml").is_file())
check("mixed: non-els xml -> dest",
      (dest2 / "police3_hi.xml").is_file() and not (els_target / "police3_hi.xml").exists())

# setting OFF -> xml goes to the destination folder (old behaviour)
b.setRenameXmlToEls(False)
check("toggle off", b.property("renameXmlToEls") is False)
check("toggle persisted", config.Config.load().rename_xml_to_els is False)
xml2 = sandbox / "xmlonly2"
xml2.mkdir()
(xml2 / "FBI2.xml").write_bytes(ELS_XML)
b.renameDrop([str(xml2)])
check("off: dest needed again", b.property("renameNeedsDest") is True)
b.renameExecute("police4")
check("off: xml -> dest", (dest2 / "police4.xml").is_file()
      and not (els_target / "police4.xml").exists())
b.setRenameXmlToEls(True)

# setting ON but no GTA path -> fall back to the destination, message logged
b.config.gta_path = ""
b.renameChanged.emit()
xml3 = sandbox / "xmlonly3"
xml3.mkdir()
(xml3 / "FBI.xml").write_bytes(ELS_XML)
b.renameDrop([str(xml3)])
check("no gta: dest needed", b.property("renameNeedsDest") is True)
b.renameExecute("police")
check("no gta: xml -> dest fallback (no data loss)", (dest2 / "police.xml").is_file())
import i18n as _i18n  # noqa: E402
check("fallback message logged",
      any(t == _i18n.T("rename_els_fallback") for _, _, t in b._history))

# ---------- 5) sidebar auto-collapse (hover) + screenshot (page index 4) ----------
shots = []
if win is not None:
    import gc
    import shiboken6
    from PySide6.QtCore import QObject, QPoint  # noqa: E402
    from PySide6.QtQuick import QQuickWindow
    from PySide6.QtTest import QTest  # noqa: E402

    win.setProperty("currentPage", 4)
    ptr = int(shiboken6.getCppPointer(win)[0])
    # shiboken returns the cached QWindow wrapper for a known address — drop it
    # first so wrapInstance can create a fresh QQuickWindow-typed wrapper.
    # (NOTE: dropping it also invalidates child wrappers obtained via findChild
    # on the old wrapper — re-find children on qwin afterwards.)
    win = None
    gc.collect()
    qwin = shiboken6.wrapInstance(ptr, QQuickWindow)
    sb = qwin.findChild(QObject, "sidebar")

    def pump(secs: float) -> None:
        end = time.time() + secs
        while time.time() < end:
            app.processEvents()
            time.sleep(0.01)

    check("sidebar auto-collapse default off", b.property("sidebarAutoCollapse") is False)
    check("sidebar expanded by default", sb is not None and sb.property("width") == 224)
    b.setSidebarAutoCollapse(True)
    pump(0.5)
    check("auto on: collapsed", sb.property("width") == 70)
    QTest.mouseMove(qwin, QPoint(60, 300))
    pump(0.5)
    check("hover: expands", sb.property("width") == 224)
    QTest.mouseMove(qwin, QPoint(700, 300))
    pump(0.5)
    check("unhover: collapses", sb.property("width") == 70)
    check("auto-collapse persisted", config.Config.load().sidebar_auto_collapse is True)
    b.setSidebarAutoCollapse(False)
    pump(0.4)
    check("auto off: manual state restored", sb.property("width") == 224)

    def grab_and_quit():
        img = qwin.grabWindow()
        out = sandbox / "_verify_rename.png"   # keep artifacts out of the repo
        img.save(str(out))
        shots.append(out)
        app.quit()

    QTimer.singleShot(700, grab_and_quit)   # wait out the 150ms page fade
    QTimer.singleShot(8000, app.quit)       # hard stop
    app.exec()
check("screenshot grabbed", bool(shots and shots[0].is_file()))

print("OK" if not failures else f"{len(failures)} check(s) failed: {failures}")
sys.exit(1 if failures else 0)

