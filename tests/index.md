---
title: Testing
layout: default
---

# Introduction

Even at an early stage in the project, the complexity has risen to the point that bugs cause side effects. To mitigate this, tests are being added to this project.

---

# Test Exectution

Most tests here are `pytest` tests. They can be executed directly by providing the path to test file or with `poetry run pytest -v` to run all tests. Execute this command from the base project directory.

3rd party testing tools have also been integrated into this projectL:

Testing Software |
[flake8]()

---

# Unit Tests

---

## Fixture

- Fixture: [The tests/conftest.conf](/tests/conftest.py)
- Test file: [/tests/conftest.py](/tests/conftest.py)
- Test functions:
  - `sample_candle()`
  - `sample_instrument()`
  - `db_mgr()`

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
  - `make_candle()`
  - `test_candle_key_is_sortable_timestamp_string()`
  - `test_to_dict_does_not_include_candle_key()`
  - `test_from_db_round_trips_from_to_dict()`
  - `test_from_oanda_builds_candle()`

  ---

## Instrument Tests

- Module: [/aifx/forex/Instrument](/aifx/forex/Instrument.py)
- Test file: [/tests/unit/test_instrument.py()](/tests/unit/test_instrument.py)
- Test functions:
  - `make_instrument()`
  - `test_to_dict()`
  - `test_from_db_round_trip()`
  - `test_from_oanda()`
