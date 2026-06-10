#!/usr/bin/env bash
# Build the Medical-Supply ERP manuals: DOCX + HTML on the host, then render the
# PDFs with WeasyPrint inside the Odoo container (correct Arabic RTL/bidi).
# The Arabic PDF embeds the Alexandria font (same Arabic font applied to the
# system via the Spiffy theme).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> build DOCX + HTML (from docs/manual/_content/*.json)"
python3 scripts/build_manual.py

echo "==> copy Alexandria fonts into the container"
docker compose exec -T odoo mkdir -p /tmp/fonts
docker cp scripts/fonts/Alexandria-Regular.ttf ephem-app:/tmp/fonts/Alexandria-Regular.ttf
docker cp scripts/fonts/Alexandria-Bold.ttf    ephem-app:/tmp/fonts/Alexandria-Bold.ttf

echo "==> render PDFs with WeasyPrint"
for L in EN AR; do
  docker cp "docs/manual/_manual_${L}.html" "ephem-app:/tmp/manual_${L}.html"
  docker compose exec -T odoo python3 -m weasyprint "/tmp/manual_${L}.html" "/tmp/manual_${L}.pdf"
  docker cp "ephem-app:/tmp/manual_${L}.pdf" "docs/manual/Medical-Supply_ERP_User_Manual_${L}.pdf"
  echo "    -> docs/manual/Medical-Supply_ERP_User_Manual_${L}.pdf"
done

echo "==> done. Outputs in docs/manual/"
ls -lah docs/manual/Medical-Supply_ERP_User_Manual_*.{docx,pdf}
