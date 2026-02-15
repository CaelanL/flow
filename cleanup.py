import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flow.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

query = """SELECT id, text FROM transcriptions
WHERE text GLOB '*[一-鿿]*' OR text GLOB '*[぀-ヿ]*' OR text GLOB '*[㐀-䶿]*'"""

cur.execute(query)
rows = cur.fetchall()

if not rows:
    print("No CJK rows found.")
    sys.exit(0)

print(f"Found {len(rows)} rows:")
for r in rows:
    print(f"  [{r[0]}] {repr(r[1][:80])}")

if "--delete" in sys.argv:
    cur.execute("""DELETE FROM transcriptions
    WHERE text GLOB '*[一-鿿]*' OR text GLOB '*[぀-ヿ]*' OR text GLOB '*[㐀-䶿]*'""")
    conn.commit()
    print(f"\nDeleted {len(rows)} rows.")

conn.close()
