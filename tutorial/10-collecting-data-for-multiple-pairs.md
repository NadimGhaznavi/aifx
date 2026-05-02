---
title: FOREX Tutorial - 10 Collecting Data for Multiple Pairs
layout: default
---

# Introduction

The page covers the [10th tutorial video](https://www.youtube.com/watch?v=7rmfu1bdYCM&list=PLZ1QII7yudbecO6a-zAI6cuGP1LLnmW8e&index=10).

---

# Notes

- Create a new notebook; `save_candles.ipnb`
- Create `fetch_candles()` to fetch the data from OANDA
- Create `get_candles_df()` to convert the data to a *DataFrame*
- Create `save_file()` to save the DataFrame to disk
- Creaee `create_data()` that calls the previous three functions
- Create code to step though the valid pairs and then call the `create_data()` function to save 4000 candles worth of data to file for all valid currency pairs.