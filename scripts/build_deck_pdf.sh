#!/usr/bin/env bash
# Render the self-contained demo deck HTML to PDF using WeasyPrint inside the
# odoo container (which has WeasyPrint 69 + the font stack). The HTML inlines
# all images and fonts as base64, so no asset paths need to resolve.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build_deck.py

HTML="docs/deck/Medical-Supply_ERP_Demo_Deck.html"
PDF="docs/deck/Medical-Supply_ERP_Demo_Deck.pdf"

# Ensure WeasyPrint is present (a container recreate can drop runtime pip installs)
docker compose exec -u root -T odoo bash -lc \
  'python3 -c "import weasyprint" 2>/dev/null || (apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 >/dev/null 2>&1; pip install --break-system-packages -q weasyprint)'

docker compose cp "$HTML" odoo:/tmp/deck.html
docker compose exec -T odoo python3 -c \
  "import weasyprint; weasyprint.HTML('/tmp/deck.html').write_pdf('/tmp/deck.pdf')"
docker compose cp odoo:/tmp/deck.pdf "$PDF"

echo "Wrote $PDF"
ls -lh "$PDF"
