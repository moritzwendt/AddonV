from __future__ import annotations

from typing import Callable

from i18n import T


class ReplaceDecider:
    # Resolves "file already exists — replace?" prompts during installs. The actual
    # dialog is the in-app QML overlay: `ask` is Backend._ask, taking a spec dict and
    # returning the chosen button id. "…to all" answers are remembered for the batch.

    def __init__(
        self,
        ask: Callable[[dict], str],
        body_key: str,
        offer_all: bool = False,
        title_key: str = "replace_title",
    ) -> None:
        self._ask = ask
        self._body_key = body_key
        self._title_key = title_key
        self._offer_all = offer_all
        self._all: bool | None = None

    def __call__(self, name: str) -> bool:
        if self._all is not None:
            return self._all
        if self._offer_all:
            buttons = [
                {"id": "no_all", "label": T("no_to_all"), "kind": "ghost"},
                {"id": "no", "label": T("no"), "kind": "ghost"},
                {"id": "yes", "label": T("yes"), "kind": "solid"},
                {"id": "yes_all", "label": T("yes_to_all"), "kind": "solid"},
            ]
        else:
            buttons = [
                {"id": "no", "label": T("no"), "kind": "ghost"},
                {"id": "yes", "label": T("yes"), "kind": "solid"},
            ]
        choice = self._ask({
            "template": "message",
            "title": T(self._title_key),
            "body": T(self._body_key, name=name),
            "cancelId": "no",
            "buttons": buttons,
        })
        if choice == "yes_all":
            self._all = True
            return True
        if choice == "no_all":
            self._all = False
            return False
        return choice == "yes"
