import sqlite3, math
con = sqlite3.connect(r"C:\dev\XMotion\Analysis\XMotion.db")
cur = con.cursor()
# 2026-07-04 rescale: Ambiguity/Noise rebased to 1-99 (old doubling/linear scales retired with EST=MV/SD)
# mapping: amb 1->10, 2->25 ; noise 1.7->20. Verdicts unchanged (bands rebased in same edit).
for lid, amb, noi in ((1, 25, 20), (2, 25, 20), (3, 10, 20)):
    sd = round(math.sqrt(amb * noi), 2)
    verdict = "PASS" if sd <= 25 else ("MAYBE" if sd <= 40 else "FAIL")
    cur.execute("UPDATE listings SET ambiguity=?, noise=?, quality_sd=?, quality_verdict=? WHERE listing_id=?",
                (amb, noi, sd, verdict, lid))
con.commit()
print(cur.execute("SELECT listing_id, ambiguity, noise, quality_sd, quality_verdict FROM listings").fetchall())
con.close()
