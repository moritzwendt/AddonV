"""Grab verification screenshots: all 6 pages (icon regression) plus the rename
tab with missing destination (red card) and right after execution (success toast).

Run with:  py -3 tests\\screenshot_rename.py
"""
from __future__ import annotations

import gc
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

sandbox = Path(tempfile.mkdtemp(prefix="addonv-shot-"))
os.environ["USERPROFILE"] = str(sandbox)
os.environ["HOME"] = str(sandbox)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QUICK_BACKEND"] = "software"

cfg_dir = sandbox / ".addonv"
cfg_dir.mkdir(parents=True)
(cfg_dir / "config.json").write_text(json.dumps({
    "language": "de", "auto_check_updates": False, "save_terminal_history": False,
}), encoding="utf-8")

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

app = QApplication([])

import config
import backend as backend_mod
importlib.reload(config)
importlib.reload(backend_mod)
assert str(config.CONFIG_FILE).startswith(str(sandbox))

b = backend_mod.Backend()

engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("backend", b)
engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
assert engine.rootObjects()

src_dir = sandbox / "mod"
src_dir.mkdir()
for n in ("FBI.ytd", "FBI.yft", "FBI_hi.yft", "FBI+hi.ytd", "FBI.xml", "FBI_hi.xml",
          "carcols.xml", "readme.txt"):
    (src_dir / n).write_bytes(b"x")
b.renameDrop([str(src_dir)])

win = engine.rootObjects()[0]

import shiboken6
from PySide6.QtQuick import QQuickWindow
ptr = int(shiboken6.getCppPointer(win)[0])
win = None
gc.collect()
qwin = shiboken6.wrapInstance(ptr, QQuickWindow)

dest = sandbox / "out"
dest.mkdir()

steps = [
    (4, "_shot_rename_nodest.png", None),
    (4, "_shot_rename_done.png",
     lambda: (setattr(b.config, "rename_last_dest", str(dest)),
              b.renameChanged.emit(), b.renameExecute("police2"))),
    (0, "_shot_p0_install.png", None),
    (1, "_shot_p1_packs.png", None),
    (2, "_shot_p2_els.png", None),
    (3, "_shot_p3_profiles.png", None),
    (5, "_shot_p5_settings.png", None),
]


def run_step(i: int) -> None:
    if i >= len(steps):
        app.quit()
        return
    page, name, setup = steps[i]
    qwin.setProperty("currentPage", page)
    if setup is not None:
        setup()

    def grab():
        qwin.grabWindow().save(str(ROOT / name))
        print("saved", name)
        run_step(i + 1)

    QTimer.singleShot(700, grab)


QTimer.singleShot(0, lambda: run_step(0))
QTimer.singleShot(20000, app.quit)
app.exec()
