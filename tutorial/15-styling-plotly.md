---
title: FOREX Tutorial 15 - Styling Plotly
layout: default
---

# Introduction

The page covers the [15th tutorial video](https://www.youtube.com/watch?v=lfDrlOfoMLs&list=PLZ1QII7yudbecO6a-zAI6cuGP1LLnmW8e&index=17).

---

# Notes

This video covers Plotly styling:

```
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df_plot.time, open=df_plot.mid_o, high=df_plot.mid_h, low=df_plot.mid_l, close=df_plot.mid_c, line=dict(width=1), opacity=1,

))
fig.update_layout(width=1000,height=400, margin=dict(l=10, r=10, b=10, t=10),
                  font=dict(size=12,color="#e1e1e1"),
                  paper_bgcolor="#1e1e1e", plot_bgcolor="#1e1e1e")
fig.update_xaxes(
    gridcolor="#1f292f", showgrid=True, fixedrange=True, rangeslider=dict(visible=False)
)
fig.update_yaxes(
    gridcolor="#1f292f", showgrid=True, fixedrange=True
)
fig.show()
```

---

# Links

- [Plotly](https://plotly.com/python/)


[Back](/tutorial/index.html)

