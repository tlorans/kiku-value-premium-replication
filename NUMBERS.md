# NUMBERS.md — where the numbers on the site come from

The rule is that no number appears on a page unless one of the page's own
cells prints it, or the page attributes it to Kiku (2006). A number that is
neither computed nor attributed does not go on the site.

## How the rule is enforced

The site is a Quarto website, and every page runs its Python at build time.
A computed number on a page is therefore the output of the cell above it, and
it cannot drift away from the code, because there is no separate copy of it to
drift. The old version of this file was a per-number ledger, written when the
site was hand-written Markdown under a `docs/` directory and each figure was
typed into the prose by hand. That ledger is no longer needed for computed
values, and re-indexing them here would just be a third copy to keep in sync.

Two jobs do the checking. `.github/workflows/tests.yml` runs the package suite
on every push. `.github/workflows/freshness.yml` runs weekly, deletes
`site/_freeze`, and re-executes every page from scratch, so a change in the
package that moves a printed number fails the build rather than sitting
unnoticed in the committed freeze.

Reproduce the whole site offline with `make freeze`, which deletes the freeze
cache and renders everything. Run `uv run pytest` for the package gate.

## What still needs recording

Numbers quoted from the paper are the ones that no cell computes, so they are
pinned in code instead. `src/geap/lrr/estimation/goldens.py` holds every
printed cell of Bansal, Kiku, and Yaron (2016) that the site quotes:
Tables 1 to 8 with their standard errors, J-tests, and the simulated
columns of Table 4. Four pages under Long-run risks show the paper's
tables and figures with our value beside the printed one, and each page
ends with a "Where each number comes from" callout.

| Page | Paper objects | Fits the page runs |
|---|---|---|
| `site/lrr/estimation.qmd` | Tables 1 to 3, Figure 1 | the LRR grid and the No-Vol grid |
| `site/lrr/time-aggregation.qmd` | Tables 4 to 6, Figure 2 | h = 1 with six starts, h = 26, 12, 4 with three, a 20-draw Monte Carlo |
| `site/lrr/portfolios.qmd` | Table 7 | the LRR grid and the four second-stage claims |
| `site/lrr/quarterly.qmd` | Table 8 | the quarterly grid and h = 1 |

The frames come from `geap.lrr.estimation.report`; the pages wrap them in
`great_tables`. Hats print with this sample's sandwich standard errors;
the paper's are an eight-year block bootstrap. `examples/bky_jme.py`
prints the same frames. The shipped annual panel is CRSP value-weighted
NYSE/AMEX/NASDAQ (`crsp.msi`) with BLS CPI and 90-day T-bills
(`crsp.mcti`), and BEA NIPA consumption. Rebuild with
`build_annual(refresh=True)`. Market return, dividend growth, and log P/D
match Table 1 to display precision. Mean $\Delta c$ is 0.16 percent
against the printed 0.18 (NIPA revisions). The fitted ex-ante real T-bill
is 0.69 percent against the printed 0.50. The quarterly panel is real,
its dividend flow is the trailing four-quarter sum divided by four, and
its price-dividend ratio is price over that one-quarter flow, which is
the convention of the model's time-aggregated moment; the quarterly
mean log P/D therefore sits about log 4 above the annual one.

## Open caveats on the Bansal, Kiku, and Yaron replication

Each item names what differs from the paper, the size of the gap, what
was tried, and the test that pins the current state. The Kiku (2006)
grid-resolution caveat further down has the same shape.

**The J statistics are an order of magnitude smaller than the paper's.**
At the paper's own printed vectors our J is 7.2 for the LRR model
(paper 10.4), 25 for the annual specification (paper 231), and 22 for
No-Vol (paper 78.5). The rejections agree; the magnitudes do not.
Removing the autoregressive penalty in the state extraction moves the
LRR J to 16 and the annual J to 15, so the extraction is not the cause.
The weighting matrix and the covariance estimator of the paper are not
spelled out beyond "diagonal inverse variance" and Newey-West, and the
difference is unresolved. `tests/test_bky_estimate.py::test_j_at_table2_is_tens_not_thousands`
pins the LRR value.

**The CUE surface at h = 1 has several basins.** Seven starts on the
1930 to 2015 panel end at objectives between 0.31 and 0.71. The cold
start stops at persistence 0.97 with p 0.27, which is not the paper's
result. `n_starts=6` runs six generic starts that differ in the IES and
in the split of consumption risk between the persistent and the
short-run shock, and the lowest of them has persistence 0.92, risk
aversion above the LRR fit's, and p 0.02, which is the paper's
qualitative result. A start at the paper's printed Table 4 vector
reaches a lower objective still (0.31, persistence 0.87). The site
reports the lowest generic start, not the paper-seeded one.
`tests/test_bky_specs.py::test_annual_h1_multi_start_rejects_and_lowers_persistence`
pins it. The simulated columns of Table 4 are 20 draws of 86 years
from the monthly fixed-frequency fit, each fitted by the same CUE from
one start; the paper's population column has no counterpart. The
staged fit that `method="staged"` still offers piles up at the
parameter bounds on samples this short and is not used on the site.

**The No-Vol fit does not land on the paper's parameters.** The site's
three-start grid stops at h = 10 with risk aversion 16, persistence
0.995 at its upper bound, a dividend loading of 10.5 against the
printed 4.8, and p 0.06 with nine degrees of freedom; six starts reach
h = 8 with risk aversion 20 and p 0.048. The paper rejects at p 0.00.
The surface is flat in the IES (its sandwich SE is above 10). Nothing
further was tried. `tests/test_bky_specs.py::test_no_vol_gmm_from_cold_start`
pins the restriction.

**Table 7 is a weighted minimum-distance second stage, not joint GMM.**
Preferences, consumption, and the states are held at the market fit,
and each claim's four cash-flow parameters minimize a weighted distance
on the paper's moment list, including the market beta as a closed-form
decision-frequency beta. No standard errors are reported. At our market
fit the loadings and premia land near the paper's, but the simulated
CAPM beta of small minus large is about 0.4 against the printed 0.86,
with or without the beta moment; the value minus growth beta matches.
`tests/test_bky_cross_section.py::test_estimated_phi_within_two_paper_se`
pins the loadings.

**The quarterly dividend convention is ours, and Table 8 does not
reproduce the paper's contrast.** The paper does not say how it treats
quarterly dividends. Raw within-quarter real dividend growth has a
first autocorrelation near minus one half, which is payment-timing
noise the model does not have. The trailing-sum flow matches the
model's mean and volatility of the price-dividend ratio at the paper's
Table 8 vector to within 0.03 and gives dividend-growth autocorrelation
0.32 next to the model's 0.29; before the rebuild the panel was
nominal, seasonal, and on a four-quarter price-dividend convention, and
J at the printed vector was 134. On the rebuilt panel the
time-aggregation fit lands on the paper's h = 2 with objective 0.15,
but with risk aversion 18 against the printed 7.45, persistence 0.89,
and p 0.0006 against the printed 0.04. The h = 1 fit has risk aversion
7.9 against the printed 8.66 but p 0.48 against the printed 0.00. The
paper's ordering, risk aversion higher without time aggregation, is
reversed. Nothing further was tried.
`tests/test_bky_quarterly.py::test_quarterly_dividends_are_real_deseasonalised_and_within_quarter`
pins the conventions and `tests/test_bky_quarterly.py::test_quarterly_gmm_from_cold_start`
the fit.

`src/geap/lrr/empirical/goldens.py` holds Kiku's printed
values from Tables I, III, and VI, along with the 1930 to 2003 sample bounds.
`tests/test_empirical_goldens.py` checks that our reconstruction from the
shipped data lands inside the standard errors she printed. A page that
quotes a paper figure says so in its own "Where each number comes from" block.

One caveat is open, and the site states it on
`site/lrr/index.qmd`. Kiku's printed Table VII return
levels, which are 6.07, 11.36, and 7.53 with a risk-free rate of 1.58, do not
reproduce exactly from the package. The gap is grid resolution. Her 30-point
discretization of the persistent component over-disperses it by roughly 21
percent, and a grid-convergence study in
`tests/test_implications.py::test_grid_convergence` shows the solution moving
toward her printed values as the grid is refined. At 60 points the risk-free
rate lands at 1.84 against her 1.58, and the CAPM beta ratio at 0.91 against
her 0.92. The pages print the package's own values next to hers rather than
quoting hers as the model's output. `examples/dcf_counterfactual.py` states its
CAPM panel in level-free form for the same reason.

## The example scripts

Each script runs standalone with `uv run python examples/<name>.py`, and each
prints its numbers rather than writing them anywhere.

| Script | What it prints |
|---|---|
| `run_paper.py` | the whole paper, in the order Kiku presents it |
| `dcf_counterfactual.py` | the discounted cash flow counterfactual on the Table II economy, in three panels |
| `robustness.py` | the model premium as one parameter at a time is varied |
| `two_firms.py` | two synthetic firms differing only in their loading on the persistent component |
| `table_ii_calibration.py` | the Table II calibration, read from `geap.ModelParams()` at run time |
| `calibrate_any_portfolio.py` | the workflow for calibrating and pricing a cross-section you supply |
| `gmm_linear_factor.py` | just-identified and over-identified linear-factor GMM |
| `gmm_power_utility.py` | two-parameter power-utility SDF GMM on a constructed sample |
| `bky_jme.py` | Bansal, Kiku, Yaron (2016) Tables 1 to 8 and the two figures' numbers, ours beside the paper's |

## Resolved findings, kept as history

Four findings were recorded against the old site, and all four are now fixed.
They are listed because the reasoning behind each fix is still taught on the
site, and because someone reading old commits will meet the labels.

**F1, the Table VII model column.** The consumption-claim solver iterated the
Euler fixed point in a form whose local slope was 1 minus theta, which is 28,
so the iteration diverged and landed on a silent clamp. The solver now iterates
the theta-divided contraction, whose modulus is below one, integrates the
Gaussian innovations in closed form, uses genuine Tauchen-Hussey transition
weights, and raises `SolverDivergenceError` instead of flooring. The residual
level gap against Kiku's prints is the grid-resolution caveat described above.
Gated by `tests/test_implications.py`.

**F2, the equal-loading counterfactual.** The old page printed a spread of
exactly zero, while the code printed minus 0.12 percent, because the block
equalizes the loading on the persistent component but not the short-run
volatility loading or the residual correlation. The examples page prints the
real figure.

**F3, the consumption autocorrelation.** The old page claimed an annual
autocorrelation of 0.43 from 1000 simulated samples, and the code printed 0.15.
The cause was time aggregation. The paper sums 12 monthly consumption levels
and then takes log growth, which is how the national accounts build their
annual series, and that raises the autocorrelation. The old code summed monthly
log growth rates instead. The package uses the level convention.

**F4, an elasticity typed in by hand.** The old page printed 56.3 for the
market claim's price-dividend elasticity, which contradicted its own stated
inputs and the solver's 37.5. The analytical solution computes it.
