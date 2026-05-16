---
title: Testing Framework
layout: default
---

# Introduction

Even at an early stage in the project, the complexity has risen to the point that bugs cause side effects. To mitigate this, tests are being added to this project.

---

# Test Execution

Most tests here are `pytest` tests. They can be executed directly by providing the path to test file or with `poetry run pytest -v` to run all tests. Execute this command from the base project directory.

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

## Instrument Tests

- Module: [/aifx/forex/Instrument](/aifx/forex/Instrument.py)
- Test file: [/tests/unit/test_instrument.py](/tests/unit/test_instrument.py)
- Test functions:
  - `test_to_dict()`
  - `test_from_db_round_trip()`
  - `test_from_oanda()`

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
