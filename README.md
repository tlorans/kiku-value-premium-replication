# Kiku (2006) – Is the Value Premium a Puzzle?

Python package that replicates Dana Kiku’s 2006 Job Market Paper using the Bansal–Yaron long-run risks model with Epstein–Zin preferences.

The paper shows that the value premium is rational compensation for differential exposure to long-run consumption risk.

**Repository:** https://github.com/tlorans/kiku-value-premium-replication  
**Documentation (GitHub Pages):** https://tlorans.github.io/kiku-value-premium-replication/

The site is the recipe (empirical → model → calibration → implications). This README is only a pointer.

## Installation

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"
uv pip install -e ".[data]"
```

Section 2 (Table I) needs the `[data]` extra and a repo-root `.env` with `WRDS_USERNAME` and `WRDS_PASSWORD`. Without WRDS you can still solve Table II:

```bash
uv run python examples/run_paper.py
```

The example uses `n_x=15` so it finishes; the paper default is `n_x=30`.

## License

MIT
