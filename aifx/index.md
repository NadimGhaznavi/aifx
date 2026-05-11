---
title: AI FX
layout: default
---

![Qt Client](/images/qt_client.png)

---

# Architecture

- Python with PySide6 for Qt integration
- Oanda API for market data

- Standalone Broker Console Application
  - Oanda manager - Retrieval of OANDA data
  - In memory database for caching
  - ZeroMQ Server for interprocess communication

- Standalone Python Qt Application
  - Retrieves instruments from the broker
  - Sends feed request to the broker
  - Consumes and plots candlestick data

![Class Diagram](/images/aifx-class-diagram.png)
