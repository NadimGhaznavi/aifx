---
title: AI FX
layout: default
---

# Architecture

- Python with PySide6 for Qt integration

- Oanda API for market data
  - OandaMgr - Retrieval of OANDA data

- Sqlite3 for in memory and file databases
  - DbMgr - File, cursor and connection management

- CacheMgr
  - Sits between the OandaMgr and the DbMgr
  - Ensures in memory Db is fresh
  
- Plotly for candlestick and other visualizations

