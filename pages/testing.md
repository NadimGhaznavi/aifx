---
title: Testing Framework
layout: default
---

# Introduction

Even at an early stage in the project, the complexity has risen to the point that bugs cause side effects. To mitigate this, tests are being added to this project.

---

# Test Execution

Most tests here are `pytest` tests. They can be executed directly by providing the path to test file or with `poetry run pytest -v` to run all tests. Execute this command from the base project directory.

For the local project virtual environment, use:

```
aifx_venv/bin/python -m pytest -q tests/unit/test_mqclient.py tests/unit/test_clientqt_cache.py
```

3rd party testing tools have also been integrated into this project:

## flake8

- [flake8](https://flake8.pycqa.org/en/latest/)

Configuration: 

```
- (aifx_venv) dan@sally:/opt/dev/aifx$ cat .flake8
[flake8]
max-line-length = 88
extend-ignore = E203
exclude =
    .git,
    __pycache__,
    .venv,
    aifx/ui_form.py,
    aifx/client/ui_form.py
```

## mypy

- [mypy](https://mypy-lang.org/)

Configuration (from `pyproject.toml`):

```
[[tool.mypy.overrides]]
module = ["plotly", "plotly.*"]
ignore_missing_imports = true
```

## black

- [Black](https://black.readthedocs.io/en/stable/)

## isort

- [isort](https://isort.readthedocs.io/en/latest/)

---

# Unit Tests

---

## AiFxLog Tests

- Module: [/aifx/utils/AiFxLog](/aifx/utils/AiFxLog.py)
- Test file: [/tests/unit/test_aifxlog.py](/tests/unit/test_aifxlog.py)
- Test functions:
  - `test_aifxlog_uses_module_name_as_logger_client_id()`
  - `test_aifxlog_sets_configured_log_level()`
  - `test_aifxlog_adds_one_console_handler()`
  - `test_aifxlog_does_not_duplicate_console_handlers()`
  - `test_aifxlog_adds_one_file_handler()`
  - `test_aifxlog_does_not_duplicate_file_handlers()`
  - `test_loglevel_changes_logger_level()`
  - `test_invalid_log_level_raises_key_error()`
  - `test_logging_methods_accept_normal_messages()`

---

## Fixture

- Fixture: [The tests/conftest.py](/tests/conftest.py)
- Test file: [/tests/conftest.py](/tests/conftest.py)
- Test functions:
  - `sample_candle()`
  - `sample_instrument()`
  - `db_mgr()`

---

## BrokerDb Tests

- Module [/aifx/db/BrokerDb](/aifx/db/BrokerDb.py)
- Test file: [/tests/unit/test_brokerdb.py](/tests/unit/test_brokerdb.py)
- Test functions:
  - `test_get_instruments_returns_none_when_empty()`
  - `test_get_instruments_returns_instruments_sorted_by_name()`
  - `test_get_latest_candle_returns_none_when_empty()`
  - `test_get_latest_candle_returns_newest_candle_for_instrument()`
  - `test_get_recent_candles_returns_empty_list_when_empty()`
  - `test_get_recent_candles_filters_by_instrument_and_returns_oldest_first()`

---

## Broker Tests

- Module: [/aifx/mgr/Broker](/aifx/mgr/Broker.py)
- Test file: [/tests/unit/test_broker.py](/tests/unit/test_broker.py)
- Test functions:
  - `test_get_instruments_returns_cached_db_instruments()`
  - `test_get_instruments_fetches_oanda_when_cache_is_empty()`
  - `test_get_instruments_returns_empty_dict_when_no_data()`
  - `test_broker_registers_shutdown_method()`
  - `test_get_recent_candles_returns_cached_db_candles()`
  - `test_get_recent_candles_fetches_oanda_when_cache_is_empty()`
  - `test_get_recent_candles_converts_oanda_payload_to_reply_format()`
  - `test_get_recent_candles_returns_empty_list_when_no_data()`
  - `test_start_feed_creates_feed_and_background_tasks()`
  - `test_start_feed_is_idempotent_for_existing_feed()`
  - `test_shutdown_returns_ack_and_schedules_quit()`
  - `test_quit_cancels_tasks_stops_mq_and_closes_db()`
  - `test_quit_is_idempotent()`

---

## DbMgr Tests

- Module: [/aifx/db/DbMgr](/aifx/db/DbMgr.py)
- Test file: [/tests/unit/test_dbmgr.py](/tests/unit/test_dbmgr.py)
- Test functions:
  - `test_dbmgr_rejects_unknown_db_type()`
  - `test_new_cache_db_has_empty_tables()`
  - `test_select_one_returns_none_when_no_rows()`
  - `test_select_all_returns_empty_list_when_no_rows()`
  - `test_upsert_empty_records_returns_zero()`
  - `test_upsert_instrument_inserts_row()`
  - `test_upsert_instrument_updates_existing_row()`
  - `test_is_stale_returns_true_for_empty_instruments_table()`
  - `test_is_stale_rejects_table_without_stale_config()`

---

## Candle Tests

- Module: [/aifx/forex/Candle](/aifx/forex/Candle.py)
- Test file: [/tests/unit/test_candle.py](/tests/unit/test_candle.py)
- Test Functions:
  - `test_candle_key_is_sortable_timestamp_string()`
  - `test_to_dict_does_not_include_candle_key()`
  - `test_from_db_round_trips_from_to_dict()`
  - `test_from_oanda_builds_candle()`

---

## ClientDb Tests

- Module: [/aifx/db/ClientDb](/aifx/db/ClientDb.py)
- Test file: [/tests/unit/test_clientdb.py](/tests/unit/test_clientdb.py)
- Test functions:
  - `test_clientdb_get_recent_candles_returns_empty_list_when_empty()`
  - `test_clientdb_upsert_candles_accepts_candle_objects()`
  - `test_clientdb_upsert_candles_accepts_dict_records()`
  - `test_clientdb_get_recent_candles_filters_limits_and_returns_oldest_first()`
  - `test_clientdb_upsert_candles_updates_existing_row()`
  - `test_clientdb_upsert_instruments_accepts_instrument_objects()`
  - `test_clientdb_upsert_instruments_accepts_dict_records()`

---

## ClientQt Cache Tests

- Module: [/aifx/client/ClientQt](/aifx/client/ClientQt.py)
- Test file: [/tests/unit/test_clientqt_cache.py](/tests/unit/test_clientqt_cache.py)
- Test functions:
  - `test_on_instrument_changed_renders_from_client_cache()`
  - `test_on_instrument_changed_requests_broker_when_client_cache_is_empty()`
  - `test_on_recent_candles_upserts_and_renders_from_client_cache()`
  - `test_on_candle_received_upserts_and_renders_from_client_cache()`

---

## Instrument Tests

- Module: [/aifx/forex/Instrument](/aifx/forex/Instrument.py)
- Test file: [/tests/unit/test_instrument.py](/tests/unit/test_instrument.py)
- Test functions:
  - `test_to_dict()`
  - `test_from_db_round_trip()`
  - `test_from_oanda()`

---

## Feed Tests

- Module: [/aifx/utils/Feed](/aifx/utils/Feed.py)
- Test file: [/tests/unit/test_feed.py](/tests/unit/test_feed.py)
- Test functions:
  - `test_feed_stores_name_and_defaults_runtime_state()`
  - `test_feed_runtime_state_can_be_updated()`
  - `test_feed_supports_dataclass_equality_for_same_state()`

---

## MQEvent Tests

- Module: [/aifx/zmq/MQEvent](/aifx/zmq/MQEvent.py)
- Test file: [/tests/unit/test_mqevent.py](/tests/unit/test_mqevent.py)
- Test functions:
  - `test_mqevent_stores_event_type_and_defaults_optional_fields()`
  - `test_mqevent_stores_routing_id_client_id_and_payload()`
  - `test_mqevent_supports_dataclass_equality()`
  - `test_mqevent_is_frozen()`

---

## MQClient Tests

- Module: [/aifx/zmq/MQClient](/aifx/zmq/MQClient.py)
- Test file: [/tests/unit/test_mqclient.py](/tests/unit/test_mqclient.py)
- Test functions:
  - `test_mqclient_initializes_sockets_and_addresses()`
  - `test_mqclient_builds_topics()`
  - `test_mqclient_connected_uses_recent_heartbeat()`
  - `test_mqclient_heartbeat_reply_emits_broker_status_with_latency()`
  - `test_mqclient_register_subscribe_and_unsubscribe()`
  - `test_mqclient_send_serializes_message()`
  - `test_mqclient_send_returns_false_when_socket_would_block()`
  - `test_mqclient_get_instruments_sends_request()`
  - `test_mqclient_get_recent_candles_sends_request()`
  - `test_mqclient_start_feed_sends_start_feed_message()`
  - `test_mqclient_poll_control_reply_emits_instruments()`
  - `test_mqclient_poll_control_reply_emits_recent_candles()`
  - `test_mqclient_bg_sub_listen_dispatches_registered_handler()`
  - `test_mqclient_quit_closes_sockets_and_context()`

---

## MQMsg Tests

- Module: [/aifx/zmq/MQMsg](/aifx/zmq/MQMsg.py)
- Test file: [/tests/unit/test_mqmsg.py](/tests/unit/test_mqmsg.py)
- Test functions:
  - `test_mqmsg_stores_fields_and_defaults_payload_to_empty_dict()`
  - `test_mqmsg_properties_can_be_updated()`
  - `test_to_dict_includes_protocol_version()`
  - `test_to_json_returns_utf8_json_bytes()`
  - `test_from_dict_reconstructs_message()`
  - `test_from_dict_defaults_missing_target_to_none()`
  - `test_from_dict_defaults_missing_or_none_payload_to_empty_dict()`
  - `test_from_dict_rejects_non_dict_payload()`
  - `test_from_json_round_trips_from_to_json()`

---

## MQServer Tests

- Module: [/aifx/zmq/MQServer](/aifx/zmq/MQServer.py)
- Test file: [/tests/unit/test_mqserver.py](/tests/unit/test_mqserver.py)
- Test functions:
  - `test_mqserver_initializes_addresses_and_sockets()`
  - `test_mqserver_builds_topic()`
  - `test_mqserver_connected_uses_recent_heartbeat()`
  - `test_mqserver_publish_sends_topic_and_compact_json()`
  - `test_mqserver_wraps_recent_candles_handler_result_in_reply()`
  - `test_mqserver_send_serializes_message()`
  - `test_mqserver_recv_parses_message()`
  - `test_mqserver_register_client_adds_new_client_and_event()`
  - `test_mqserver_register_existing_client_updates_without_event()`
  - `test_mqserver_remove_client_removes_client_and_event()`
  - `test_mqserver_quit_returns_when_not_started()`

---

## MQMsgBatch Tests

- Module: [/aifx/zmq/MQMsgBatch](/aifx/zmq/MQMsgBatch.py)
- Test file: [/tests/unit/test_mqmsgbatch.py](/tests/unit/test_mqmsgbatch.py)
- Test functions:
  - `test_new_batch_starts_empty()`
  - `test_append_requires_lock()`
  - `test_pop_batch_requires_lock()`
  - `test_append_tracks_size_and_timeout()`
  - `test_pop_batch_returns_messages_resets_state_and_increments_batch_num()`
  - `test_batch_can_be_reused_after_pop()`

---

## MQUtils Tests

- Module: [/aifx/zmq/MQUtils](/aifx/zmq/MQUtils.py)
- Test file: [/tests/unit/test_mqutils.py](/tests/unit/test_mqutils.py)
- Test functions:
  - `test_encode_json_encodes_string_as_utf8_bytes()`
  - `test_decode_json_decodes_bytes_to_dict()`
  - `test_decode_json_decodes_zmq_frame_to_dict()`
  - `test_ensure_bytes_returns_bytes_unchanged()`
  - `test_ensure_bytes_returns_frame_bytes()`
  - `test_split_router_frames_without_empty_delimiter()`
  - `test_split_router_frames_with_empty_delimiter()`
  - `test_split_router_frames_rejects_too_few_frames()`
  - `test_ignore_zmq_teardown_suppresses_zmq_error()`
  - `test_ignore_zmq_teardown_does_not_suppress_other_errors()`

---

## OandaMgr Tests

- Module: [/aifx/mgr/OandaMgr](/aifx/mgr/OandaMgr.py)
- Test file: [/tests/unit/test_oandamgr.py](/tests/unit/test_oandamgr.py)
- Test functions:
  - `test_fetch_instruments_returns_status_and_data_on_http_200()`
  - `test_fetch_instruments_returns_none_tuple_on_non_200()`
  - `test_fetch_instruments_returns_none_tuple_on_request_exception()`
  - `test_get_instruments_returns_none_when_fetch_fails()`
  - `test_get_instruments_converts_oanda_payloads_to_instruments()`
  - `test_fetch_candles_passes_request_details_and_returns_response()`
  - `test_get_candles_returns_none_on_non_200()`
  - `test_get_candles_converts_only_complete_candles()`

---

## RecentCandlesModel Tests

- Module: [/aifx/forex/RecentCandlesModel](/aifx/forex/RecentCandlesModel.py)
- Test file: [/tests/unit/test_recentcandlesmodel.py](/tests/unit/test_recentcandlesmodel.py)
- Test functions:
  - `test_recent_candles_model_starts_empty()`
  - `test_recent_candles_model_loads_candles()`
  - `test_recent_candles_model_horizontal_headers()`
  - `test_recent_candles_model_vertical_headers_are_one_based()`
  - `test_recent_candles_model_ignores_non_display_header_roles()`
  - `test_recent_candles_model_formats_display_values()`
  - `test_recent_candles_model_aligns_display_values_right()`
  - `test_recent_candles_model_returns_none_for_invalid_index()`
  - `test_recent_candles_model_returns_none_for_unhandled_data_role()`
  - `test_recent_candles_model_clear_removes_rows()`
