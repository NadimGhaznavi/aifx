---
title: AI FX
layout: default
---

# Introduction

![Qt Client](/images/qt_client.png)

AI FX is a Python-based foreign exchange market analysis platform built around a
loosely coupled broker/client architecture.

- The *Qt Client* retrieves live market data from the *Broker* process
- The *Broker* returns market data 
  - if available in it's in memory databae or
  - it engages the *Oanda Manager* which retrieves the data over the Internet from *Oanda*
- Latency is plotted for 
  - the link between the *Qt Client* and the *Broker* and 
  - for the Internet link between the *Broker* and *Oanda*

---

# Features

- Live candlestick chart visualization
- Standalone broker process
- ZeroMQ publish/subscribe messaging
- In-memory SQLite caching layer
- PySide6 / Qt desktop client
- Real-time instrument feed subscription
- Decoupled client/server architecture

---

# Architecture

![Class Diagram](/images/aifx-class-diagram.png)

---

# Broker Process

The broker is responsible for:

- Retrieving market data from OANDA
- Managing instrument and candle feeds
- Caching recent data in an in-memory SQLite database
- Publishing candle updates over ZeroMQ

## Core Components

- `OandaMgr`
- `BrokerDb`
- `ServerMQ`

---

# Qt Client

The Qt desktop client is responsible for:

- Retrieving instruments from the broker
- Requesting live market feeds
- Consuming ZeroMQ candle streams
- Rendering live candlestick charts
- Ploting the latency of:
  - The LAN link between the Qt client and the Python Broker
  - The Internet link between the Python Broker and Oanda

## Core Components

- `ClientQt`
- `ClientMQ`
- `Plotly` candlestick visualization

---

# Technology Stack

- Python 3
- PySide6 / Qt for Python
- ZeroMQ
- SQLite3
- Plotly with Javascript
- Oanda REST API

---

# Dev Ops

- [Dev Ops](/pages/devops/index.html)
  - Version control
  - PyPI integration
  - [Testing Framework](/pages/testing.html)

---

# Demo

- [Short screengrab demo](/images/demo-v0.15.16.mp4)