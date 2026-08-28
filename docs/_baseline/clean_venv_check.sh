#!/usr/bin/env bash
# Issue 6: verify the quickstart from a CLEAN venv (no repo .venv, no cached site-packages).
set -eu
cd "$(dirname "$0")/.."
rm -rf .issue0/cleanenv
start=$(date +%s)
uv venv .issue0/cleanenv --python 3.12
uv pip install --python .issue0/cleanenv/Scripts/python.exe -e .
mid=$(date +%s)
.issue0/cleanenv/Scripts/python.exe - <<'PY'
import time
t0 = time.time()
import lrrcs as lrr
sol = lrr.solve_analytical(lrr.get_table_ii_params())
lrr.print_long_short_premium(sol)
out = lrr.price_from_loadings(1.5)   # Issue 5 snippet
print("price_from_loadings(1.5):", {k: round(v, 3) for k, v in out.items()})
print("version:", lrr.__version__)
print(f"snippet_seconds: {time.time() - t0:.1f}")
PY
end=$(date +%s)
echo "install_seconds: $((mid - start))"
echo "total_seconds: $((end - start))"
