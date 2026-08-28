---
title: Price your own claim
nav_order: 8
---

# Price your own claim

Bring a dividend process. The model returns the price-dividend ratio and the expected return. The loadings are estimated from cash flows alone — never from returns.

The recipe has three steps. Project dividend growth on the two-year moving average of consumption ([Measuring leverage]({{ '/measuring-leverage.html' | relative_url }}), equation (19)); the slope is the loading \\(\phi\\). Hand the loading to `lrr.price_from_loadings`. Read off the price-dividend elasticity to \\(x_t\\) and the compensation for \\(x_t\\)-news. Returns never enter.

Two synthetic firms, identical except the loading (output of `examples/two_firms.py`):

```text
firm     phi      A1  premium_lr %   g_eff %  gordon %
A        0.5    -3.0         -0.03      3.20      6.89
B        1.5    15.2          0.14      3.32      7.01
```

The loading is the only difference between the rows, and nothing was re-tuned between them. Firm B's dividends track the persistent component of consumption: its price-dividend ratio moves with long-run news (\\(A_1 = 15.2\\)) and its compensation for that news is positive (0.14 percent a year). Firm A's dividends lean the other way — its loading sits below the household's \\(1/\psi\\), its ratio moves against the news (\\(A_1 = -3.0\\)), and the \\(x_t\\)-news compensation is slightly negative. A hedge pays less. The Gordon column, which sees only expected growth, puts the two firms 0.12 points apart. The wedge is the risk in the cash flows, and `premium_lr` is the \\(x_t\\)-news piece of it; short-run and volatility news add more.

Price your own series:

```python
import lrrcs as lrr

# loading of your dividend growth on the consumption MA,
# measured from cash flows (Measuring leverage, eq. 19)
phi = 1.5

out = lrr.price_from_loadings(phi)
print(out["A1"], out["premium_lr"])
```

[Installation]({{ '/installation.html' | relative_url }}).
