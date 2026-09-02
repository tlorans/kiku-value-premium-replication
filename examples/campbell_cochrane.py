"""Campbell and Cochrane (1999) external habit.

Run: uv run python examples/campbell_cochrane.py
"""
import geap


def main():
    model = geap.CampbellCochraneModel()
    res = model.solve()
    print(res.summary())
    power = geap.PowerUtilityModel(gamma=2).solve()
    print("habit premium", res.compare("equity", "bill").premium)
    print("power gamma=2 premium", power.compare("equity", "bill").premium)


if __name__ == "__main__":
    main()
