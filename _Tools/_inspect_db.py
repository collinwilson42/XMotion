import sqlite3
con = sqlite3.connect(r"C:\dev\XMotion\Analysis\XMotion.db")
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
views = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
print("TABLES:", tables)
print("VIEWS:", views)
if "budget_allocations" in tables:
    print("BUDGETS:", cur.execute("SELECT b.month, v.name, b.credits_allocated FROM budget_allocations b JOIN vas v ON v.va_id=b.va_id").fetchall())
if "shots" in tables:
    print("SHOTS rows:", cur.execute("SELECT COUNT(*) FROM shots").fetchone()[0])
    print("SHOTS cols:", [r[1] for r in cur.execute("PRAGMA table_info(shots)")])
print("VAS:", cur.execute("SELECT va_id, name, initials, status FROM vas").fetchall() if any(r[1]=="initials" for r in cur.execute("PRAGMA table_info(vas)")) else cur.execute("SELECT va_id, name, status FROM vas").fetchall())
print("LISTINGS rows:", cur.execute("SELECT COUNT(*) FROM listings").fetchone()[0])
print("CONFIG:", cur.execute("SELECT key, value FROM config").fetchall())
con.close()
