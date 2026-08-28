#!/usr/bin/env bash
# Issue 0: fetch rendered HTML of every live page into docs/_baseline/html/
set -u
base="https://tlorans.github.io/kiku-value-premium-replication"
cd "$(dirname "$0")/.." || exit 1
mkdir -p docs/_baseline/html
ok=0; fail=0
for p in index getting-started long-run-risks-model measuring-leverage time-series cross-section package installation api financial-data; do
  if [ "$p" = "index" ]; then url="$base/"; else url="$base/$p.html"; fi
  curl -sL --max-time 60 "$url" -o "docs/_baseline/html/$p.html"
  size=$(wc -c < "docs/_baseline/html/$p.html")
  title=$(grep -o '<title>[^<]*</title>' "docs/_baseline/html/$p.html" | head -1)
  echo "$p: $size bytes | $title"
  case "$title" in *404*|*"not found"*) fail=$((fail+1));; *) ok=$((ok+1));; esac
done
echo "fetched_ok=$ok fetch_404=$fail"
