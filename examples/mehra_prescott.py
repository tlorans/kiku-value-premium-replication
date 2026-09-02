"""Mehra and Prescott (1985) two-state CCAPM.

Run: uv run python examples/mehra_prescott.py
"""
import geap


def main():
    model = geap.PowerUtilityModel()
    res = model.solve()
    print(res.summary())
    print(model.replace(gamma=2).solve().compare("equity", "bill").summary())
    levered = geap.PowerUtilityModel(claims={"high": {"phi": 3}}).solve()
    print(levered.compare("high", "bill").summary())


if __name__ == "__main__":
    main()
