---
title: FOREX Tutorial 12 - Oanda API
layout: default
---

# Introduction

The page covers the [12th tutorial video](https://www.youtube.com/watch?v=wg5herWaV4M&list=PLZ1QII7yudbecO6a-zAI6cuGP1LLnmW8e&index=14).

---

# Notes

- Create an `OandaAPI()` class that:
  - Sets up a session
  - Implements
    - `fetch_instruments()` - Fetch instruments data from Oanda
    - `get_instruments_df()` - Load instruments data frames from file
    - `save_instruments()` - Save instruments to file
    - `fetch_candles()` - Fetch candle data from Oanda

- I introduced a number of *constants* files to eliminate the *magic strings* in the tutorial code. My code is now slightly different than that shown in the tutorial.

---

[Back](/tutorial/index.html)