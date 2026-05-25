# tests/unit/test_dbserver.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from dataclasses import asdict

from aifx.constants.DDb import (DbNumRowsRequest, DbSelectAllRequest,
                                DbSelectOneRequest, DbUpsertRequest)
from aifx.constants.DDb import DColCandles as C_CAND
from aifx.constants.DDb import DColInstrument as C_INST
from aifx.constants.DDb import DTable as TABLE
from aifx.constants.DMethod import DMethod as METHOD
from aifx.db.DbServer import DbServer
from aifx.zmq.MQMsg import MQMsg


def _server(tmp_path) -> DbServer:
    return DbServer(log_file=None, db_file=str(tmp_path / "db.sqlite3"))


def _msg(method: str, payload: dict) -> MQMsg:
    return MQMsg(
        sender="test",
        target="DbServer",
        method=method,
        payload=payload,
    )


def test_dbserver_upsert_and_num_rows(tmp_path, sample_instrument) -> None:
    server = _server(tmp_path)
    try:
        upsert_payload = asdict(
            DbUpsertRequest(
                table=TABLE.INSTRUMENTS,
                records=[sample_instrument.to_dict()],
                key_fields=[C_INST.NAME],
            )
        )

        result = server.upsert(_msg(METHOD.UPSERT, upsert_payload))

        assert result == {"rows": 1}
        assert server.num_rows(
            _msg(METHOD.NUM_ROWS, asdict(DbNumRowsRequest(table=TABLE.INSTRUMENTS)))
        ) == {"rows": 1}
    finally:
        server.db.close()


def test_dbserver_select_all_and_select_one(tmp_path, sample_candle) -> None:
    server = _server(tmp_path)
    try:
        record = sample_candle.to_dict()
        server.upsert(
            _msg(
                METHOD.UPSERT,
                asdict(
                    DbUpsertRequest(
                        table=TABLE.CANDLES,
                        records=[record],
                        key_fields=[
                            C_CAND.INSTRUMENT,
                            C_CAND.GRANULARITY,
                            C_CAND.Y,
                            C_CAND.MO,
                            C_CAND.D,
                            C_CAND.H,
                            C_CAND.MI,
                            C_CAND.S,
                        ],
                    )
                ),
            )
        )

        select_all = server.select_all(
            _msg(
                METHOD.SELECT_ALL,
                asdict(
                    DbSelectAllRequest(
                        table=TABLE.CANDLES,
                        where=f"{C_CAND.INSTRUMENT} = ?",
                        params=[sample_candle.instrument],
                        order_by=f"{C_CAND.Y} DESC",
                        limit=10,
                    )
                ),
            )
        )
        select_one = server.select_one(
            _msg(
                METHOD.SELECT_ONE,
                asdict(
                    DbSelectOneRequest(
                        table=TABLE.CANDLES,
                        where=f"{C_CAND.INSTRUMENT} = ?",
                        params=[sample_candle.instrument],
                    )
                ),
            )
        )

        assert select_all == {"records": [record]}
        assert select_one == {"record": record}
    finally:
        server.db.close()
