# aifx/constants/DPairs.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0from typing import Final

from typing import Final


class DPair:

    AUD_JPY: Final[str] = "AUD_JPY"
    AUD_USD: Final[str] = "AUD_USD"
    CAD_JPY: Final[str] = "CAD_JPY"
    EUR_GBP: Final[str] = "EUR_GBP"
    EUR_JPY: Final[str] = "EUR_JPY"
    EUR_USD: Final[str] = "EUR_USD"
    GBP_AUD: Final[str] = "GBP_AUD"
    GBP_JPY: Final[str] = "GBP_JPY"
    GBP_USD: Final[str] = "GBP_USD"
    NZD_JPY: Final[str] = "NZD_JPY"
    NZD_USD: Final[str] = "NZD_USD"
    USD_BRL: Final[str] = "USD_BRL"
    USD_CAD: Final[str] = "USD_CAD"
    USD_CHF: Final[str] = "USD_CHF"
    USD_JPY: Final[str] = "USD_JPY"
    USD_MXN: Final[str] = "USD_MXN"
    USD_TRY: Final[str] = "USD_TRY"
    USD_ZAR: Final[str] = "USD_ZAR"


DPairHghVol = [
    DPair.AUD_USD,
    DPair.EUR_GBP,
    DPair.EUR_JPY,
    DPair.EUR_USD,
    DPair.GBP_JPY,
    DPair.GBP_USD,
    DPair.NZD_USD,
    DPair.USD_CAD,
    DPair.USD_CHF,
    DPair.USD_JPY,
]

DPairVolatile = [
    DPair.AUD_JPY,
    DPair.CAD_JPY,
    DPair.EUR_GBP,
    DPair.GBP_AUD,
    DPair.GBP_JPY,
    DPair.NZD_JPY,
    DPair.USD_BRL,
    DPair.USD_MXN,
    DPair.USD_TRY,
    DPair.USD_ZAR,
]
