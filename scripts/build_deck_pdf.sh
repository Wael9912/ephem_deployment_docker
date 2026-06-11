#!/usr/bin/env bash
# Render the self-contained demo deck HTML to PDF using WeasyPrint inside the
# odoo container (which has WeasyPrint 69 + the font stack). The HTML inlines
# all images and fonts as base64, so no asset paths need to resolve.
# Builds BOTH languages: EN (LTR) and AR (RTL, Arabic screenshots).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build_deck.py en
python3 scripts/build_deck.py ar

# Ensure WeasyPrint is present (a container recreate can drop runtime pip installs)
docker compose exec -u root -T odoo bash -lc \
  'python3 -c "import weasyprint" 2>/dev/null || (apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 >/dev/null 2>&1; pip install --break-system-packages -q weasyprint)'

for L in EN AR; do
  HTML="docs/deck/Medical-Supply_ERP_Demo_Deck_${L}.html"
  PDF="docs/deck/Medical-Supply_ERP_Demo_Deck_${L}.pdf"
  docker compose cp "$HTML" "odoo:/tmp/deck_${L}.html"
  docker compose exec -T odoo python3 -c \
    "import weasyprint; weasyprint.HTML('/tmp/deck_${L}.html').write_pdf('/tmp/deck_${L}.pdf')"
  docker compose cp "odoo:/tmp/deck_${L}.pdf" "$PDF"
  echo "Wrote $PDF"
  ls -lh "$PDF"
done
