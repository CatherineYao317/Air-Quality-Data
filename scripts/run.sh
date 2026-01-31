
should_generate：`report/executive.html`

---

## D) `scripts/run.sh`（一键跑）
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> Run bare-bones analysis"
python analysis/00_smoke_test.py

echo "==> Render Quarto report to single HTML"
quarto render report/executive.qmd

echo "==> Confirm output exists"
test -f report/executive.html
echo "OK: report/executive.html generated"
