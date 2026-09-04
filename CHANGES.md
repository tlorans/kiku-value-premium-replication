# Changes

## 1.4.0

Bansal, Kiku, and Yaron (2016) GMM estimation of long-run risks with
time aggregation, under `geap.lrr.estimation`. The estimator takes the
annual panel and a Bansal–Yaron (2004) start; Table 2 is the comparison
after GMM, not an input. Continuously updated diagonal GMM weights,
Hansen Lemma 4.2 $J$-test (raw-parameter Jacobian, QR-stabilized),
sandwich standard errors, and an optional
eight-year moving-block bootstrap in `geap.gmm`. Quarterly starts
rescale the Bansal–Yaron monthly vector by decisions per year (four
samples), not as if \(h\) were annual. `bootstrap_h` re-selects \(h\)
on each bootstrap draw. Kiku (2006) calibration and quadrature solver
are unchanged.

## 1.3.0

Hansen GMM as `geap.gmm`: `estimate`, `linear_factor`, power-utility
SDF moments, two-step weights, Newey-West standard errors, and the
J-test. Cash-flow `calibrate_claim` is unchanged. Docs under GMM.

## 1.2.0

External habit as a third family: `geap.CampbellCochraneModel`,
defaulting to Campbell and Cochrane (1999). Docs under Habit.

## 1.1.0

Power-utility CCAPM as a second family: `geap.PowerUtilityModel`,
defaulting to Mehra and Prescott (1985). Docs under Power utility.

## 1.0.0

The package was renamed from lrrcs to geap. `import lrrcs` no longer
works. Use `import geap`. Long-run risks is the first family, under
`geap.lrr`, with a shared `AssetPricingModel` protocol for later
families. The documentation is a library site, not a course.
