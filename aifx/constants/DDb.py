# aifx/constants/DDb.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import dataclass, field
from typing import Any, Final

from aifx.constants.DInstrument import DInstrumentF as INSF
from aifx.constants.DMethod import DMethod as METHOD


class DColInstrument:
    NAME: Final[str] = "name"
    TYPE: Final[str] = "type"
    DISPLAY_NAME: Final[str] = "display_name"
    PIP_LOCATION: Final[str] = "pip_location"
    MARGIN_RATE: Final[str] = "margin_rate"
    UPDATED_Y: Final[str] = "updated_y"
    UPDATED_MO: Final[str] = "updated_mo"
    UPDATED_D: Final[str] = "updated_d"
    UPDATED_H: Final[str] = "updated_h"
    UPDATED_MI: Final[str] = "updated_mi"
    UPDATED_S: Final[str] = "updated_s"


class DColCandles:
    INSTRUMENT = INSF.INSTRUMENT
    GRANULARITY: Final[str] = "granularity"
    Y: Final[str] = "y"
    MO: Final[str] = "mo"
    D: Final[str] = "d"
    H: Final[str] = "h"
    MI: Final[str] = "mi"
    S: Final[str] = "s"
    CANDLE_KEY: Final[str] = "candle_key"
    VOLUME: Final[str] = "volume"
    MID_O: Final[str] = "mid_o"
    MID_H: Final[str] = "mid_h"
    MID_L: Final[str] = "mid_l"
    MID_C: Final[str] = "mid_c"
    BID_O: Final[str] = "bid_o"
    BID_H: Final[str] = "bid_h"
    BID_L: Final[str] = "bid_l"
    BID_C: Final[str] = "bid_c"
    ASK_O: Final[str] = "ask_o"
    ASK_H: Final[str] = "ask_h"
    ASK_L: Final[str] = "ask_l"
    ASK_C: Final[str] = "ask_c"


class DDbF:
    BRAIN: Final[str] = "brain"
    BROKER: Final[str] = "broker"
    CACHE: Final[str] = "cache"
    DB_SERVER: Final[str] = "db_server"
    FILE: Final[str] = "file"
    LIMIT: Final[str] = "limit"
    MEMORY: Final[str] = ":memory:"
    OANDA: Final[str] = "oanda"
    SERVER_MQ: Final[str] = "db_server_mq"
    SERVER_MQ_MSGS: Final[str] = "db_server_mq_messages"


# ----- These are the payloads for the SQL over MQ requests ----


class DDbMqOps:
    NUM_ROWS = METHOD.NUM_ROWS
    SELECT_ALL = METHOD.SELECT_ALL
    SELECT_ONE = METHOD.SELECT_ONE
    UPSERT = METHOD.UPSERT


@dataclass(slots=True, frozen=True)
class DbNumRowsRequest:
    table: str


@dataclass(slots=True, frozen=True)
class DbSelectAllRequest:
    table: str
    where: str | None = None
    params: list[Any] = field(default_factory=list)
    order_by: str | None = None
    limit: int | None = None


@dataclass(slots=True, frozen=True)
class DbSelectOneRequest:
    table: str
    where: str | None = None
    params: list[Any] = field(default_factory=list)
    order_by: str | None = None


@dataclass(slots=True, frozen=True)
class DbUpsertRequest:
    table: str
    records: list[dict[str, Any]]
    key_fields: list[str]


class DTable:
    CANDLES: Final[str] = "candles"
    INSTRUMENTS: Final[str] = "instruments"
    LATENCY: Final[str] = "latency"
