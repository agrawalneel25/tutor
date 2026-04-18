"""Runtime config: shared JMC constants + per-user overrides from user.config.json.

Import from here; do not import `shared` directly in most places.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .shared import (
    PANOPTO_HOST,
    BLACKBOARD_HOST,
    BB_COOKIE_ALLOWLIST,
    PANOPTO_DEFAULT_LANG,
    SUBJECTS,
    SUBJECT_SLUGS,
    SubjectMeta,
    subject,
)

REPO = Path(__file__).resolve().parents[2]
AUTH_DIR = REPO / "auth_state"
PANOPTO_STATE = AUTH_DIR / "panopto.json"
BLACKBOARD_STATE = AUTH_DIR / "blackboard.json"
SUBJECTS_DIR = REPO / "subjects"
WEBUI_DIR = REPO / "webui"

USER_CONFIG_PATH = REPO / "user.config.json"

AUTH_DIR.mkdir(exist_ok=True)


@dataclass
class Preferences:
    hint_style: str = "progressive"  # progressive | on_demand | none
    reveal_solution_immediately: bool = False
    teach_mode: str = "full"  # full | brief
    web_port: int = 8787


@dataclass
class UserConfig:
    name: str = "Student"
    email: str = ""
    preferences: Preferences = field(default_factory=Preferences)
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "UserConfig":
        if not USER_CONFIG_PATH.exists():
            return cls()
        raw = json.loads(USER_CONFIG_PATH.read_text())
        prefs = Preferences(**(raw.get("preferences") or {}))
        return cls(
            name=raw.get("name", "Student"),
            email=raw.get("email", ""),
            preferences=prefs,
            extras={k: v for k, v in raw.items() if k not in {"name", "email", "preferences"}},
        )

    def save(self) -> None:
        raw: dict[str, Any] = {
            "name": self.name,
            "email": self.email,
            "preferences": {
                "hint_style": self.preferences.hint_style,
                "reveal_solution_immediately": self.preferences.reveal_solution_immediately,
                "teach_mode": self.preferences.teach_mode,
                "web_port": self.preferences.web_port,
            },
            **self.extras,
        }
        USER_CONFIG_PATH.write_text(json.dumps(raw, indent=2))


USER = UserConfig.load()


__all__ = [
    "PANOPTO_HOST", "BLACKBOARD_HOST", "BB_COOKIE_ALLOWLIST", "PANOPTO_DEFAULT_LANG",
    "SUBJECTS", "SUBJECT_SLUGS", "SubjectMeta", "subject",
    "REPO", "AUTH_DIR", "PANOPTO_STATE", "BLACKBOARD_STATE", "SUBJECTS_DIR", "WEBUI_DIR",
    "USER_CONFIG_PATH", "Preferences", "UserConfig", "USER",
]
