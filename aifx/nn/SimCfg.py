# aifx/utils/SimCfg.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com/
#    License: GPL 3.0

from __future__ import annotations

from typing import Any, Callable, ClassVar
import traceback

from aifx.constants.DBrain import DBrainF as BRAINF


class SimCfg:
    _DEFAULTS: ClassVar[dict[str, Any]] = {
        BRAINF.START_TS: -1,
        BRAINF.STOP_TS: -1,
        
    }

    _COERCE: ClassVar[dict[str, Callable[[Any], Any]]] = {
        BRAINF.START_TS: float,
        BRAINF.STOP_TS: float,
    }

    __slots__ = ("_values",)

    def __init__(self, values: dict[str, Any] | None = None) -> None:
        self._values: dict[str, Any] = dict(self._DEFAULTS)
        if values:
            self.apply(values)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SimCfg":
        return cls(payload)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def apply(self, payload: dict[str, Any]) -> None:
        for key, value in payload.items():
            self.set(key, value)

    def get(self, key: str) -> Any:
        if key not in self._DEFAULTS:
            raise KeyError(f"Unknown cfg key: {key}")
        return self._values[key]

    def set(self, key: str, value: Any) -> None:
        if key not in self._DEFAULTS:
            raise KeyError(f"Unknown cfg key: {key}")

        coerce = self._COERCE.get(key)
        try:
            self._values[key] = coerce(value) if coerce else value
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"STACKTRACE: {traceback.format_exc()}")
