# Changes

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
