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
pinned in code instead. `src/geap/lrr/empirical/goldens.py` holds Kiku's printed
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
