# aifx/constants/DNetwork.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from typing import Final


class DNetwork:
    BROKER_HOSTNAME: Final[str] = "localhost"
    BROKER_PORT: Final[int] = 20101
    BROKER_HB_PORT: Final[int] = 20102
    BROKER_PUB_PORT: Final[int] = 20103


class DNetworkF:
    TCP: Final[str] = "tcp://"
