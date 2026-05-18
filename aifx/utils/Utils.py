# aifx/utils/Utils.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0


def format_latency_ms(latency_ms: float | None) -> str:
    if latency_ms is None:
        return ""

    if latency_ms < 10:
        return f"{latency_ms:.3f} ms"

    if latency_ms < 1000:
        return f"{latency_ms:.0f} ms"

    return f"{latency_ms / 1000:.4f} s"
