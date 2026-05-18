# tests/unit/test_clientqt_cache.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

from types import SimpleNamespace
from unittest.mock import MagicMock

from aifx.client.ClientQt import ClientQt
from aifx.constants.DDef import DDef as DEF
from aifx.constants.DMQ import DMQ as MQ
from aifx.constants.DMQ import DMQF as MQF


class FakeComboBox:
    def __init__(self, value):
        self.value = value

    def currentData(self):
        return self.value


def _client_shell(client_db, sample_instrument):
    mq = SimpleNamespace(
        candle_topic=MagicMock(return_value="aifx.candles.USD_CAD"),
        get_recent_candles=MagicMock(return_value=True),
        register_sub_handler=MagicMock(),
        start=MagicMock(),
        subscribe=MagicMock(),
        start_feed=MagicMock(),
        topic=MagicMock(return_value="aifx.oanda_latency"),
    )
    return SimpleNamespace(
        _active_instrument=None,
        _active_topic=None,
        _instruments={sample_instrument.name: sample_instrument.to_dict()},
        client_db=client_db,
        clear_data=MagicMock(),
        log=SimpleNamespace(
            info=MagicMock(),
            warning=MagicMock(),
            debug=MagicMock(),
        ),
        mq=mq,
        on_candle_received=MagicMock(),
        render_candles=MagicMock(),
        ui=SimpleNamespace(
            cb_instrument=FakeComboBox(sample_instrument.name),
            lbl_current_pair=SimpleNamespace(
                setStyleSheet=MagicMock(),
                setText=MagicMock(),
            ),
        ),
    )


def test_on_instrument_changed_renders_from_client_cache(
    db_mgr, sample_candle, sample_instrument
) -> None:
    from aifx.db.ClientDb import ClientDb

    client_db = ClientDb(db_mgr=db_mgr)
    client_db.upsert_candles([sample_candle])
    client = _client_shell(client_db=client_db, sample_instrument=sample_instrument)

    ClientQt.on_instrument_changed(client)

    client.render_candles.assert_called_once_with(
        topic="aifx.candles.USD_CAD",
        candles=[sample_candle],
    )
    client.mq.get_recent_candles.assert_not_called()


def test_on_instrument_changed_requests_broker_when_client_cache_is_empty(
    db_mgr, sample_instrument
) -> None:
    from aifx.db.ClientDb import ClientDb

    client = _client_shell(
        client_db=ClientDb(db_mgr=db_mgr),
        sample_instrument=sample_instrument,
    )

    ClientQt.on_instrument_changed(client)

    client.render_candles.assert_not_called()
    client.mq.get_recent_candles.assert_called_once_with(
        topic="aifx.candles.USD_CAD",
        instrument=sample_instrument.to_dict(),
        count=DEF.MAX_PLOTLY_CANDLES,
    )


def test_on_recent_candles_upserts_and_renders_from_client_cache(
    db_mgr, sample_candle
) -> None:
    from aifx.db.ClientDb import ClientDb

    client = SimpleNamespace(
        _active_instrument="USD_CAD",
        _active_topic="aifx.candles.USD_CAD",
        client_db=ClientDb(db_mgr=db_mgr),
        log=SimpleNamespace(debug=MagicMock(), warning=MagicMock()),
        render_candles=MagicMock(),
    )

    ClientQt.on_recent_candles(
        client,
        topic="aifx.candles.USD_CAD",
        candles=[sample_candle.to_dict()],
    )

    client.render_candles.assert_called_once_with(
        topic="aifx.candles.USD_CAD",
        candles=[sample_candle],
    )


def test_on_candle_received_upserts_and_renders_from_client_cache(
    db_mgr, sample_candle
) -> None:
    from aifx.db.ClientDb import ClientDb

    client = SimpleNamespace(
        _active_topic="aifx.candles.USD_CAD",
        client_db=ClientDb(db_mgr=db_mgr),
        log=SimpleNamespace(debug=MagicMock(), warning=MagicMock()),
        render_cached_candles=MagicMock(),
    )

    ClientQt.on_candle_received(
        client,
        topic="aifx.candles.USD_CAD",
        candle=sample_candle.to_dict(),
    )

    cached = client.client_db.get_recent_candles("USD_CAD")
    assert cached == [sample_candle]
    client.render_cached_candles.assert_called_once_with(
        topic="aifx.candles.USD_CAD",
        instrument="USD_CAD",
    )


def test_start_mq_subscribes_to_oanda_latency_topic() -> None:
    mq = SimpleNamespace(
        register_sub_handler=MagicMock(),
        start=MagicMock(),
        subscribe=MagicMock(),
        topic=MagicMock(return_value="aifx.oanda_latency"),
    )
    client = SimpleNamespace(
        log=SimpleNamespace(info=MagicMock()),
        mq=mq,
        on_oanda_latency_received=MagicMock(),
    )

    ClientQt.start_mq(client)

    mq.start.assert_called_once_with()
    mq.topic.assert_called_once_with(MQ.OANDA_LATENCY_TOPIC)
    mq.register_sub_handler.assert_called_once_with(
        "aifx.oanda_latency",
        client.on_oanda_latency_received,
    )
    mq.subscribe.assert_called_once_with("aifx.oanda_latency")


def test_on_oanda_latency_received_updates_label() -> None:
    client = SimpleNamespace(
        ui=SimpleNamespace(lbl_oanda_status=SimpleNamespace(setText=MagicMock()))
    )

    ClientQt.on_oanda_latency_received(
        client,
        topic="aifx.oanda_latency",
        data={MQF.OANDA_LATENCY: 12.3456},
    )

    client.ui.lbl_oanda_status.setText.assert_called_once_with("12.35 ms")
