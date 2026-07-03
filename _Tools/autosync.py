"""
autosync.py - XMotion repo auto-synchronizer.

Each cycle (default every 5 minutes):
    1. git pull --rebase --autostash     (take remote changes first)
    2. git add -A + commit               (only if local changes exist)
    3. git push                          (publish)

This is safer than alternating pull-only / push-only cycles: you are never
more than one interval stale, and you never push over an unpulled change.

Usage:
    py autosync.py            # 5-minute loop
    py autosync.py -10        # 10-minute loop  (XCopy-style flag)
    py autosync.py --once     # single cycle, then exit (smoke test)

Single-writer rule: only ONE machine should run autosync while XMotion.db is
tracked - git cannot merge a binary. If a VA machine ever needs autosync,
gitignore the .db there first.

Conflict policy: if the rebase hits a conflict, we ABORT the rebase (repo
returns to a clean state), log an ALERT, and keep cycling. Nothing is lost -
local commits stay local until a human resolves. Check autosync.log.
"""
import subprocess, sys, time, os
from datetime import datetime
from pathlib import Path

REPO = Path(r"C:\dev\XMotion")
LOG = REPO / "_Tools" / "autosync.log"
LOCK = REPO / "_Tools" / "autosync.lock"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def git(*args, ok_codes=(0,)):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    return r.returncode, out

def cycle():
    # 1. pull (rebase, autostash handles a dirty tree)
    code, out = git("pull", "--rebase", "--autostash", "origin", "main")
    if code != 0:
        log(f"ALERT pull failed - aborting rebase and holding local state:\n{out}")
        git("rebase", "--abort")
        return
    if "Already up to date" not in out and out:
        log(f"pull: {out.splitlines()[-1]}")

    # 2. commit local changes if any
    code, status = git("status", "--porcelain")
    if status:
        git("add", "-A")
        n = len(status.splitlines())
        code, out = git("commit", "-m",
                        f"autosync {datetime.now().strftime('%Y-%m-%d %H:%M')} ({n} change{'s' if n != 1 else ''})")
        if code != 0:
            log(f"ALERT commit failed:\n{out}")
            return
        log(f"committed {n} change(s)")

    # 3. push (only if we are ahead)
    code, ahead = git("rev-list", "--count", "origin/main..HEAD")
    if code == 0 and ahead.strip() not in ("", "0"):
        code, out = git("push", "origin", "main")
        if code != 0:
            log(f"ALERT push failed (will retry next cycle):\n{out}")
        else:
            log(f"pushed {ahead.strip()} commit(s)")
    # nothing to do -> stay silent (keeps the log readable)

def main():
    minutes = 5
    once = "--once" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("-") and a[1:].isdigit():
            minutes = int(a[1:])

    if LOCK.exists():
        log(f"another autosync appears to be running (lock: {LOCK}). "
            "Delete the lock file if that is stale.")
        sys.exit(1)
    LOCK.write_text(str(os.getpid()))
    log(f"autosync start - every {minutes}m ({'single cycle' if once else 'loop'}), repo {REPO}")
    try:
        while True:
            cycle()
            if once:
                break
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        log("autosync stopped (Ctrl+C)")
    finally:
        LOCK.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
