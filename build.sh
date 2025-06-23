#!/usr/bin/env bash
set -o errexit

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Waiting for database..."
# Wait for database to become available (best effort)
python << END
import time, os
import psycopg2
for _ in range(10):
    try:
        print("Trying to connect to DB...")
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        conn.close()
        break
    except Exception as e:
        print(f"DB not ready yet: {e}")
        time.sleep(3)
END

echo "==> Running migrations"
if [ ! -d "migrations" ]; then
    flask db init
fi

flask db migrate -m "Render migration" || true
flask db upgrade
