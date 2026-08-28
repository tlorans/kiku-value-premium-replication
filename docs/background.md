---
title: Background & glossary
nav_order: 11
---

# Background & glossary

Three short primers for readers who have not met the pieces, and the terms the site uses. No numbers here beyond definitions; every claim lives on the page that earns it.

## Epstein-Zin preferences

Most asset pricing assumes power utility, where one number does two jobs: how much you dislike risk and how willing you are to move consumption across time. Epstein-Zin preferences split the two. Risk aversion \\(\gamma\\) says how much you would pay to avoid a gamble; the elasticity of intertemporal substitution \\(\psi\\) says how strongly you rearrange consumption when interest rates move. The price of the split is that marginal utility depends not only on tomorrow's consumption but on the return on total wealth — news about the entire future. That single change is what lets small, persistent news about growth carry a large price. Full statement: [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}).

## The long-run risks model

Consumption growth is not white noise. Bansal and Yaron split it into a small, highly persistent component \\(x_t\\) plus transitory noise, with volatility that moves slowly too. A shock to \\(x_t\\) is not news about this year; it is news about the next decade. An Epstein-Zin household that prefers early resolution of uncertainty demands compensation for holding claims whose cash flows fall on that news — and dividends inherit \\(x_t\\) through their loading \\(\phi\\). Premia and valuations come out of one solution. See [the model chapter]({{ '/long-run-risks-model.html' | relative_url }}) and [Kiku's economy]({{ '/getting-started.html' | relative_url }}).

## Why the CAPM misses low-frequency risk

The CAPM prices covariance with the market's *one-period* return. Market returns are dominated by transitory price fluctuations, so a beta near one says little about how a claim behaves when news arrives about the next decade of consumption. A claim can be a strong hedge in the short run — beta below one — and still carry a large premium for its exposure to long-run news. The model reproduces exactly this configuration, which is why the econometrician's regression prints a puzzle the household does not see: [Value versus growth]({{ '/cross-section.html' | relative_url }}).

## Glossary

| Term | Meaning |
|:---|:---|
| loading (\\(\phi\\)) | how hard a claim's dividend growth moves with the persistent component of consumption; the model's characteristic, measured from cash flows |
| persistent component (\\(x_t\\)) | the slow-moving deviation of expected consumption growth from its mean |
| P/D ratio | price per unit of annual dividend; its log is the site's valuation gauge |
| beta | slope of a claim's return on the market's return (CAPM) |
| EIS (\\(\psi\\)) | elasticity of intertemporal substitution: response of consumption plans to interest rates |
| risk aversion (\\(\gamma\\)) | willingness to pay to avoid consumption risk |
| Euler equation | \\(E_t[M_{t+1}R_{i,t+1}]=1\\): no asset is a free lunch relative to the household's marginal utility |
| cash-flow news | revision in expected dividends |
| discount-rate news | revision in expected returns |
| Table II | Kiku's calibrated economy: preferences, consumption process, and the three claims' cash-flow parameters |
