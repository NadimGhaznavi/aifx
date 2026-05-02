# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Website
  - Created a CNAME record to publish this repo as https://aifx.osoyalce.com
  - Configured the GitHub repo to publish under the DNS name
  - Created a skeleton website
- Watched and took notes:
  - [01 - Introduction](https://www.youtube.com/watch?v=zKk2iuuNJO0&list=PLZ1QII7yudbecO6a-zAI6cuGP1LLnmW8e&index=1) and [notes](https://aifx.osoyalce.com/tutorial/01-introduction.html)
- Added `tutorial` and `tutorial-code` that tracks the per-episode update data.
- Created a [web frontend](/tutorial/index.html) site.

### Code Artifacts

- images/ - Website images
- tutorial/ - GFM docs
- tutorial-code/
- his_data/ - Cache of data from OANDA
- defs.py - Project constants
- instrument.ipynb - ETL instrument data from OANDA
- save_candles.ipynb - ETL candle data from OANDA
- text.ipynb - Core Jupyter run-code-book
- utils.py - `get_his_data_filename()` and `get_instruments_data_filename()` functions

---

## [0.0.2] - 2026-04-16 @ 23:51

### Added
- GitHub actions workflow to publish to PyPI: `pip install aifx`
- `aifx` skeleton script