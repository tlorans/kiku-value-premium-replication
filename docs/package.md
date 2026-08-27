---
title: Package
nav_order: 7
has_children: true
has_toc: false
---

# Package

`lrrcs` maps the low-frequency risks embodied in cash flows into **asset prices and risk premia**. The inputs are consumption growth and dividend growth; the outputs are valuations and ex-ante compensations, for the aggregate market and for the legs of a sort. Average returns never enter the cash-flow step — they are what the model gets graded on.

```python
import numpy as np
import polars as pl
import lrrcs as lrr
```

Read the argument first: [The result]({{ '/getting-started.html' | relative_url }}), [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}), [Measuring leverage]({{ '/measuring-leverage.html' | relative_url }}), [The Time Series]({{ '/time-series.html' | relative_url }}), [The Cross Section]({{ '/cross-section.html' | relative_url }}).

Rebuild the 1930–2003 sample only if you need to: [Financial data]({{ '/financial-data.html' | relative_url }}).

- [Installation]({{ '/installation.html' | relative_url }})
- [Financial data]({{ '/financial-data.html' | relative_url }})
- [API]({{ '/api.html' | relative_url }})
