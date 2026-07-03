"""
xmotion_add_headers.py - Skill-header patcher (bridge script, wiz-9)
Adds/merges skill-format YAML frontmatter (name, description, tools, growth)
into every operational doc in C:\\dev\\XMotion. ASCII-only header text.

- Backs up every file to _Tools\\_header_backup\\ before touching it.
- Merges into existing frontmatter: existing keys are NEVER overwritten,
  new keys are appended before the closing ---.
- Collapses stacked double frontmatter blocks (Budget-Tracking bug) into one.
- Prepends a fresh block where no frontmatter exists (the handoff).
- Idempotent: re-running adds nothing that is already present.

Run:  py xmotion_add_headers.py
"""

import re
import shutil
from pathlib import Path

ROOT = Path(r"C:\dev\XMotion")
BACKUP = ROOT / "_Tools" / "_header_backup"

FM_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.S)

# fields[key] = single-line value (string) OR list (rendered as YAML list)
SPECS = {
    "AI Skills/XMotion-Account-Buildout-WBS.md": {
        "growth": [
            "Expand each segment into its own build per rollout order (Segment 10)",
            "Populate memory slots 11-30 as findings accumulate (Segment 2.2 hygiene rule)",
            "Fold S-grid analytics and DB triggers back into Segments 5 and 9 as they go live",
        ],
    },
    "AI Skills/XMotion-Higgsfield-Walkthrough.md": {
        "name": "XMotion Higgsfield Walkthrough",
        "description": "The canonical production craft skill for turning still listing photos into cinematic walkthrough videos in Higgsfield. Use when writing or reviewing a generation prompt, choosing a camera preset for a room, diagnosing warping or drift, or stitching clips into a final walkthrough. Trigger on walkthrough, Higgsfield, preset, camera move, prompt, clip, stitch, or any video generation step. Covers the two rules (no people, slow camera), the preset-to-room map, prompt templates with guardrails, clip length spec, and the per-listing production loop.",
        "tools": "filesystem",
        "growth": [
            "Findings log: dated entries per model test, preset that warps, prompt fix that held",
            "Preset performance ranking once model MV is assigned (first production session)",
            "Per-room prompt template refinements from real render results",
        ],
    },
    "AI Skills/XMotion-Shot-Protocol.md": {
        "name": "XMotion Shot Protocol",
        "type": "ai-skill",
        "status": "live",
        "growth": [
            "Slated to expand into the first-in-line Operating Protocol skill (WBS Segment 3, decision D-1)",
            "Tracking engine migrates from CSV to XMotion.db per Analysis/XMotion-DB-Schema.md",
            "Add identity, dual-register, and session-rhythm sections on expansion",
        ],
    },
    "AI Skills/XMotion-Shot-Quality-Equation.md": {
        "name": "XMotion Shot Quality Equation",
        "description": "The canonical scoring contract and listing gate. Use when scoring a captured photo set, scouting a capture block off disk, ranking Higgsfield models, or deciding pass/maybe/fail before any credits are spent. Trigger on score, scout, grade, SD, EST, quality, gate, or any capture-block review. Defines EST = MV / SD, the ambiguity doubling scale (1-16), the linear noise scale (1-5), the SD listing gate verdicts, and the step-by-step scouting protocol over TN_ thumbnails.",
        "tools": "filesystem",
        "growth": [
            "Lock EST gate thresholds once model MV is assigned (open item, WBS 4.3)",
            "Tune noise and ambiguity rubric anchors against more real capture blocks",
            "Auto-noise estimation from edge size and JPEG quantization in a later parser pass",
            "Amenity tag at capture time so segmentation is recorded, not inferred",
        ],
    },
    "Onboarding/Week 1 - Quick Start Guide.md": {
        "name": "XMotion Week 1 Onboarding",
        "description": "Week-1 workstation setup track for new VAs. Use when onboarding a new team member, walking through app or MCP installation, fixing a config issue, or re-verifying a VA workstation. Trigger on setup, onboarding, week 1, install, config, MCP, or a VA first session. Covers core app installs, team accounts, windows-mcp keystone setup, the C:/dev/XMotion workspace, Obsidian vault, the XCopy capture tool, filesystem access, and the sourcing and scoring loops.",
        "growth": [
            "Week 2 production guide: first generation session with Higgsfield",
            "Fold in the VA capture-location decision once resolved (VPS vs local, D-2)",
            "Move shared credentials out of this doc to a secure channel before any repo sync",
        ],
    },
    "Analysis/XMotion-DB-Schema.md": {
        "growth": [
            "Ship _Tools/xmotion_db.py bootstrap and smoke-test into a live XMotion.db",
            "Decide re-offer conversion policy (first-offer-only vs any-accept)",
            "Seed locations from Location Tracking and Notes when formalized",
            "Optional 3.5 s-per-image band if finer pacing resolution is wanted",
        ],
    },
    "Analysis/XMotion-Optimal Budget-Tracking.md": {
        "name": "XMotion Budget and Tracking",
        "type": "ai-skill",
        "status": "active",
        "growth": [
            "Single owner of the tracking engine per WBS 4.1; Shot-Protocol will point here",
            "CSV engine migrates to XMotion.db per Analysis/XMotion-DB-Schema.md",
            "Economics tiers and per-VA capacity modeling as volume scales past two VAs",
        ],
    },
    "_Handoffs/2026-06-27_XMotion-Session.md": {
        "name": "XMotion Handoff 2026-06-27",
        "type": "handoff",
        "status": "active-until-superseded",
        "description": "Session handoff from 2026-06-27. Load for continuity when resuming XMotion work: first-walkthrough production task on block PM_3-59_4-04, the 48hr Higgsfield trial window, open decisions D-2 (VA capture location) and MV model ranking, and parked items.",
    },
}


def render_field(key, val):
    if isinstance(val, list):
        lines = [f"{key}:"]
        lines += [f"  - {item}" for item in val]
        return "\n".join(lines)
    return f"{key}: {val}"


def existing_keys(fm_body):
    keys = set()
    for line in fm_body.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:", line)
        if m:
            keys.add(m.group(1))
    return keys


def patch(text, fields):
    """Collapse stacked frontmatter blocks, merge new fields, return new text."""
    bodies = []
    rest = text
    while True:
        m = FM_RE.match(rest)
        if not m:
            break
        bodies.append(m.group(1))
        rest = rest[m.end():]

    merged = "\n".join(bodies).strip("\n") if bodies else ""
    have = existing_keys(merged)
    additions = [render_field(k, v) for k, v in fields.items() if k not in have]

    if not additions and len(bodies) <= 1:
        return None  # nothing to do

    parts = [merged] if merged else []
    parts += additions
    new_fm = "---\n" + "\n".join(parts) + "\n---\n"
    if not bodies:
        new_fm += "\n"
    return new_fm + rest


def main():
    BACKUP.mkdir(parents=True, exist_ok=True)
    report = []
    for rel, fields in SPECS.items():
        p = ROOT / rel
        if not p.exists():
            report.append(f"MISSING   {rel}")
            continue
        raw = p.read_text(encoding="utf-8-sig")
        new = patch(raw, fields)
        if new is None:
            report.append(f"NO-CHANGE {rel}")
            continue
        shutil.copy2(p, BACKUP / p.name)
        p.write_text(new, encoding="utf-8")
        report.append(f"PATCHED   {rel}")
    print("\n".join(report))
    print(f"\nBackups in: {BACKUP}")


if __name__ == "__main__":
    main()
