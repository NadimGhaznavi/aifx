# tests/unit/test_clientqt_cache.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from aifx.client.ClientQt import ClientQt
from aifx.client.ClientQt import LATENCY_PLOT_POINTS
from aifx.constants.DDb import DDbF as DBF
from aifx.constants.DDb import DTable as TABLE
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


def test_on_oanda_latency_received_records_latency_and_updates_plot() -> None:
    client = SimpleNamespace(
        db_mgr=SimpleNamespace(add_latency=MagicMock()),
        oanda_latency_web_view=MagicMock(),
        update_latency_plot=MagicMock(),
    )

    ClientQt.on_oanda_latency_received(
        client,
        topic="aifx.oanda_latency",
        data={MQF.OANDA_LATENCY: 12.3456},
    )

    client.db_mgr.add_latency.assert_called_once_with(elem="oanda", latency=12.3456)
    client.update_latency_plot.assert_called_once_with(
        elem="oanda",
        web_view=client.oanda_latency_web_view,
    )


def test_set_connection_status_records_broker_latency() -> None:
    mq = SimpleNamespace(get_instruments=MagicMock())
    client = SimpleNamespace(
        _was_connected=True,
        broker_latency_web_view=MagicMock(),
        db_mgr=SimpleNamespace(add_latency=MagicMock()),
        mq=mq,
        update_latency_plot=MagicMock(),
    )

    ClientQt.set_connection_status(client, connected=True, latency_ms=1.25)

    client.db_mgr.add_latency.assert_called_once_with(elem=DBF.BROKER, latency=1.25)
    client.update_latency_plot.assert_called_once_with(
        elem=DBF.BROKER,
        web_view=client.broker_latency_web_view,
    )
    mq.get_instruments.assert_not_called()


def test_set_connection_status_requests_instruments_on_first_connect() -> None:
    mq = SimpleNamespace(get_instruments=MagicMock())
    client = SimpleNamespace(
        _was_connected=False,
        broker_latency_web_view=MagicMock(),
        db_mgr=SimpleNamespace(add_latency=MagicMock()),
        mq=mq,
        update_latency_plot=MagicMock(),
    )

    ClientQt.set_connection_status(client, connected=True, latency_ms=None)

    client.db_mgr.add_latency.assert_not_called()
    client.update_latency_plot.assert_not_called()
    mq.get_instruments.assert_called_once_with()
    assert client._was_connected is True


def test_set_connection_status_marks_disconnected_without_ui_labels() -> None:
    mq = SimpleNamespace(get_instruments=MagicMock())
    client = SimpleNamespace(
        _was_connected=True,
        db_mgr=SimpleNamespace(add_latency=MagicMock()),
        mq=mq,
        update_latency_plot=MagicMock(),
    )

    ClientQt.set_connection_status(client, connected=False)

    client.db_mgr.add_latency.assert_not_called()
    client.update_latency_plot.assert_not_called()
    mq.get_instruments.assert_not_called()
    assert client._was_connected is False


def test_latency_plot_html_configures_title_legend_and_current_latency() -> None:
    html = ClientQt.latency_plot_html(SimpleNamespace(), "Broker")

    assert 'text: "Broker"' in html
    assert "showlegend: true" in html
    assert 'x: 0' in html
    assert 'xanchor: "left"' in html
    assert 'y: 1' in html
    assert 'yanchor: "top"' in html
    assert "const currentLatency = y.length ? y[y.length - 1] : null;" in html
    assert "name: formatLatency(currentLatency)" in html


def test_update_latency_plot_uses_latest_points_in_time_order() -> None:
    rows = [
        {"ts": ts, "latency_ms": float(ts)}
        for ts in range(LATENCY_PLOT_POINTS + 5)
    ]
    selected_rows = list(reversed(rows[-LATENCY_PLOT_POINTS:]))
    page = SimpleNamespace(runJavaScript=MagicMock())
    web_view = SimpleNamespace(page=MagicMock(return_value=page))
    db_mgr = SimpleNamespace(select_all=MagicMock(return_value=selected_rows))
    client = SimpleNamespace(db_mgr=db_mgr)

    ClientQt.update_latency_plot(client, elem=DBF.OANDA, web_view=web_view)

    db_mgr.select_all.assert_called_once_with(
        table=TABLE.LATENCY,
        where="elem = ?",
        params=(DBF.OANDA,),
        order_by="ts DESC",
        limit=LATENCY_PLOT_POINTS,
    )
    js = page.runJavaScript.call_args.args[0]
    payload = json.loads(js.removeprefix("updateLatency(").removesuffix(");"))
    assert payload[0]["ts"] == 5
    assert payload[-1]["ts"] == LATENCY_PLOT_POINTS + 4
    assert all(point["ts"] != 4 for point in payload)
