# aifx/constants/DDef.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0


from typing import Final


class DDef:
    ACCOUNT_ID: Final[str] = "101-002-30861672-001"
    API_KEY: Final[str] = (
        "ed99def09cb58baca2b74884defa6f0a-d0ac2b598bb7a28fb4358a1b77686bc9"
    )
    OANDA_URL: Final[str] = "https://api-fxpractice.oanda.com/v3"
    SECURE_HEADER: Final[dict] = {"Authorization": f"Bearer {API_KEY}"}
