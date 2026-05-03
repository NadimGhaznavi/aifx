---
title: AI FX
layout: default
---

![AI FX Banner](/images/aifx-banner.png)

---

# Tutorial to AI FX 

## Slow file based pickle cache for market data

### Fix

  - Use Sqlite in memory DB (1 file == max_oanda_fetch)
  - Keep 4 files in memory

