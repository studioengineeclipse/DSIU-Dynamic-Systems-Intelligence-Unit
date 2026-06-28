"""Config — the watch configuration object."""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import DAEMON_STATE_DIR, DEFAULT_INTERVAL


@dataclass
class WatchConfig:
    path: str
    name: "str | None" = None
    include_docs: bool = False
    interval: int = DEFAULT_INTERVAL
    uef_path: "str | None" = None
    state_dir: str = DAEMON_STATE_DIR
    oil_state_dir: str = "dsiu_state"
    shell_state_dir: str = "dsiu_shell_state"
    record_no_change: bool = False  # watch: write every no_change, not just the first

    def display_name(self) -> str:
        import os
        return self.name or os.path.basename(self.path.rstrip("/")) or "system"

    def slug(self) -> str:
        s = re.sub(r"[^a-z0-9]+", "-", self.display_name().lower()).strip("-")
        return s or "system"
