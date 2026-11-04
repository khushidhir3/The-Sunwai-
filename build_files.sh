#!/bin/bash
echo "=== Vercel Build Step ==="
# Try installing requirements with break-system-packages (for PEP 668 / uv managed Python)
python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || true
python3 manage.py collectstatic --noinput 2>/dev/null || true
echo "=== Vercel Build Finished ==="
exit 0
