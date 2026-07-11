<#
.SYNOPSIS
    WIZX Graph Sync v2 — the jobs graphify does NOT do for itself.

.DESCRIPTION
    √1 North Star: one graph, spanning every repo + the DB schema + the vault,
    never stale, for under $2/month total.

    Author: wiz-9   Revised: 2026-07-11

    ── READ THIS: WHAT THIS SCRIPT IS *NOT* FOR ───────────────────────────────
    Keeping the CODE graph fresh is NOT this script's job. Graphify does that
    itself, better, for free:

        graphify hook install     # git post-commit -> graph rebuilds. AST only.

    Event-driven beats a cron. Your graph is never more than one commit stale
    instead of up to 24 hours stale. Run `.\wizx_graph_sync.ps1 -InstallHooks`
    once and then STOP thinking about the code graph.

    This script exists for the three things graphify genuinely cannot do alone:

      1. Dump XMotion.db's SCHEMA to .sql so it can be graphed at all
         (graphify skips binary .db files entirely — they're "not classified")
      2. Run the PAID vault pass with a cost ESTIMATE and a SPEND GUARD in front
         (left alone, graphify finds DEEPSEEK_API_KEY in your env and just spends)
      3. Re-register the global cross-repo graph (not automatic)

    ── COST ──────────────────────────────────────────────────────────────────
      PASS A  code (--update)   AST, local              $0.00  always
      PASS B  schema dump       sqlite3 .schema         $0.00  always
      PASS C  vault semantic    DeepSeek V4-Flash      ~$0.30  first run only
                                                        ~$0.00  after (cached)

    Pass C requires -Semantic. You ask for it, every time. No exceptions.

.EXAMPLE
    .\wizx_graph_sync.ps1 -InstallHooks       # ONCE. Then code stays fresh free.
    .\wizx_graph_sync.ps1                      # code + schema. $0.00.
    .\wizx_graph_sync.ps1 -Semantic -DryRun    # estimate the vault. Spends nothing.
    .\wizx_graph_sync.ps1 -Semantic            # actually ingest the vault. ~$0.30.
#>

[CmdletBinding()]
param(
    # Install git post-commit hooks so the code graph self-updates. Run once.
    [switch]$InstallHooks,

    # Run the PAID vault pass. Off by default, on purpose.
    [switch]$Semantic,

    # Estimate and print. Send nothing. Spend nothing.
    [switch]$DryRun,

    [ValidateSet('deepseek', 'ollama')]
    [string]$Backend = 'deepseek',

    [int]$TokenBudget = 8000
)

$ErrorActionPreference = 'Continue'

# ── REPOS ──────────────────────────────────────────────────────────────────
# code_only  = pure code. Pass A only. Always free.
# hybrid     = code AND vault markdown. Pass A free + Pass C paid.
#
# DELIBERATELY ABSENT: C:\dev\nautilus_trader-develop (the framework root).
# That's a vendor library you consume, not code you own. Graphing it would bury
# your own 2,495 nodes under tens of thousands of Nautilus internals. Add it only
# if you start modifying core Nautilus.
$REPOS = @(
    @{ alias='trading';     path='C:\dev\nautilus_trader-develop\dashboard'; kind='code_only' }
    @{ alias='ai_strategy'; path='C:\dev\ai_strategy';                       kind='code_only' }
    @{ alias='binura';      path='C:\dev\Binura';                            kind='code_only' }
    @{ alias='fibonacci';   path='C:\dev\fibonacci_strategy';                kind='code_only' }
    @{ alias='xmotion';     path='C:\dev\XMotion';                           kind='hybrid'    }
)

$XMOTION_DB = 'C:\dev\XMotion\XMotion.db'
$SCHEMA_DIR = 'C:\dev\XMotion\_schema'
$SCHEMA_SQL = "$SCHEMA_DIR\xmotion_schema.sql"
$LOG        = 'C:\dev\XMotion\_Handoffs\graph_sync.log'

# DeepSeek V4-Flash per 1M tokens, as of 2026-07-11. Re-verify before trusting.
$PRICE_IN  = 0.14
$PRICE_OUT = 0.28

# Ignore patterns. Written BEFORE any build, every run. This is the cost shield.
$IGNORE_CODE = @(
    '*.md','*.mdx','*.txt','*.rst','*.pdf','*.yaml','*.yml','*.html','*.ndjson',
    '*.png','*.jpg','*.jpeg','*.webp','*.gif','*.svg','*.ico','*.mp3','*.wav',
    '*.mp4','*.mov','*.ttf','*.woff','*.woff2',
    '*.mq5','*.mqh',
    'node_modules/','dist/','target/','.venv/','__pycache__/','.vercel/','.git/'
)
# XMotion is hybrid — markdown is the POINT there, so it is NOT ignored.
# But media and private credentials absolutely are.
$IGNORE_HYBRID = @(
    '*.png','*.jpg','*.jpeg','*.webp','*.gif','*.svg','*.ico',
    '*.mp4','*.mov','*.mp3','*.wav','*.ttf',
    '_Private/','node_modules/','.venv/','__pycache__/','.git/'
)

New-Item -ItemType Directory -Force -Path (Split-Path $LOG) | Out-Null
function Log { param($m,$c='White')
    $l = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $l -ForegroundColor $c; Add-Content -Path $LOG -Value $l
}

Log "=== WIZX GRAPH SYNC v2 ===" Magenta
if ($DryRun)        { Log "DRY RUN — nothing sent, nothing spent." Yellow }
if (-not $Semantic) { Log "Code + schema only. Cost: `$0.00." Cyan }

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
    Log "FATAL: graphify not on PATH. Open a NEW shell (or: uv tool update-shell)." Red
    exit 1
}

function Ensure-Ignore {
    param($repo, $patterns)
    # .claudeignore — stops graphify's own output from nuking Claude Code's
    # prompt cache and forcing a paid full re-upload. Cheap insurance.
    $ci = Join-Path $repo '.claudeignore'
    $have = if (Test-Path $ci) { Get-Content $ci } else { @() }
    foreach ($p in @('graph.json','graphify-out/')) {
        if ($p -notin $have) { Add-Content -Path $ci -Value $p }
    }
    # .graphifyignore — the actual cost shield. Nothing here reaches a paid pass.
    $gi = Join-Path $repo '.graphifyignore'
    $have = if (Test-Path $gi) { Get-Content $gi } else { @() }
    $add = $patterns | Where-Object { $_ -notin $have }
    if ($add) { Add-Content -Path $gi -Value $add; return $add.Count }
    return 0
}

# ===========================================================================
# HOOKS — run once. Then the code graph maintains ITSELF, free, on every commit.
# ===========================================================================
if ($InstallHooks) {
    Log "--- Installing git post-commit hooks (AST only, no API cost)" Cyan
    foreach ($r in $REPOS) {
        if (-not (Test-Path $r.path)) { Log "  skip $($r.alias) — missing" Yellow; continue }
        if (-not (Test-Path (Join-Path $r.path '.git'))) {
            Log "  skip $($r.alias) — not a git repo, hook needs one" Yellow; continue
        }
        Push-Location $r.path
        try {
            $pat = if ($r.kind -eq 'hybrid') { $IGNORE_HYBRID } else { $IGNORE_CODE }
            Ensure-Ignore $r.path $pat | Out-Null   # shield BEFORE the hook can fire
            & graphify hook install 2>&1 | Out-Null
            Log "  $($r.alias): hook installed" Green
        } catch { Log "  $($r.alias) hook FAILED: $($_.Exception.Message)" Red }
        finally { Pop-Location }
    }
    Log "Code graphs now self-update on every git commit. Free. Done." Green
    Log "NOTE: hooks are AST-only per graphify docs. Watch the log anyway." DarkGray
}

# ===========================================================================
# PASS A — CODE. Local AST. Free. Always.
# ===========================================================================
Log "--- PASS A: code (AST, local, `$0.00)" Cyan

foreach ($r in $REPOS) {
    if (-not (Test-Path $r.path)) { Log "  skip $($r.alias) — path missing" Yellow; continue }

    Push-Location $r.path
    try {
        $pat = if ($r.kind -eq 'hybrid') { $IGNORE_HYBRID } else { $IGNORE_CODE }
        $n = Ensure-Ignore $r.path $pat
        if ($n) { Log "  $($r.alias): +$n ignore rules" DarkGray }

        # For the hybrid repo we do NOT run the plain code pass here — its
        # markdown is in scope, so it belongs to Pass C. Running `graphify .`
        # on it now would fire an UNGUARDED semantic pass. Skip it.
        if ($r.kind -eq 'hybrid') {
            Log "  $($r.alias): deferred to Pass C (hybrid repo)" DarkGray
            continue
        }

        $out = & graphify . --update 2>&1 | Out-String

        # TRIPWIRE. A semantic pass must NEVER fire in the code pass. If it does,
        # an ignore rule has a hole and you are being billed for it, silently.
        if ($out -match 'semantic extraction') {
            Log "  !! $($r.alias): SEMANTIC PASS FIRED DURING CODE PASS." Red
            Log "  !! .graphifyignore has a hole. THIS COSTS MONEY. Investigate." Red
        }

        if ($out -match 'graph\.json: (\d+) nodes, (\d+) edges') {
            Log "  $($r.alias): $($Matches[1]) nodes / $($Matches[2]) edges" Green
        } else {
            Log "  $($r.alias): unchanged" DarkGray
        }
        & graphify cluster-only . --no-label 2>&1 | Out-Null
    }
    catch { Log "  $($r.alias) FAILED: $($_.Exception.Message)" Red }
    finally { Pop-Location }
}

# ===========================================================================
# PASS B — DB SCHEMA. Free.
#
# graphify CANNOT read XMotion.db. A .db is a binary blob; it gets skipped as
# "not classified", same as a .ttf. But graphify CAN read .sql as text.
#
# `.schema` emits DDL ONLY — CREATE TABLE, columns, FKs, view definitions.
# ZERO ROWS. No listings, no addresses, no client data, no scores. Just shape.
#
# Payoff: your 8 tables + 8 views become graph nodes, wired to the Python that
# reads and writes them. That's the code<->schema join. It's the whole point.
# ===========================================================================
Log "--- PASS B: DB schema (`$0.00)" Cyan

if (Test-Path $XMOTION_DB) {
    if (Get-Command sqlite3 -ErrorAction SilentlyContinue) {
        New-Item -ItemType Directory -Force -Path $SCHEMA_DIR | Out-Null
        if ($DryRun) {
            Log "  [dry] would dump schema -> $SCHEMA_SQL" DarkGray
        } else {
            & sqlite3 $XMOTION_DB ".schema" | Set-Content -Path $SCHEMA_SQL -Encoding UTF8
            $n = (Get-Content $SCHEMA_SQL | Measure-Object -Line).Lines
            Log "  schema: $n lines -> $SCHEMA_SQL" Green
        }
    } else {
        Log "  sqlite3 missing. Install: winget install SQLite.SQLite" Yellow
        Log "  (Pass B is a nice-to-have; the rest still works without it.)" DarkGray
    }
} else {
    Log "  XMotion.db not found at $XMOTION_DB — skipping" Yellow
}

# ===========================================================================
# PASS C — VAULT SEMANTIC. THE ONLY PASS THAT SPENDS MONEY.
# ===========================================================================
if (-not $Semantic) {
    Log "--- PASS C: SKIPPED (no -Semantic flag)" DarkGray
    Log "--- Refreshing global graph" Cyan
    foreach ($r in $REPOS) {
        $gj = Join-Path $r.path 'graphify-out\graph.json'
        if (Test-Path $gj) { & graphify global add "$gj" --as $r.alias 2>&1 | Out-Null }
    }
    & graphify global list 2>&1 | ForEach-Object { Log "  $_" }
    Log "=== DONE. Spend this run: `$0.00 ===" Green
    exit 0
}

$hybrid = $REPOS | Where-Object { $_.kind -eq 'hybrid' } | Select-Object -First 1
$root   = $hybrid.path
Log "--- PASS C: vault semantic  [$($hybrid.alias)]  [backend: $Backend]" Yellow

if (-not (Test-Path $root)) { Log "  $root missing. Abort." Red; exit 1 }

# --- ESTIMATE BEFORE SPENDING. NON-NEGOTIABLE. -----------------------------
$md = Get-ChildItem -Path $root -Include *.md,*.txt,*.sql -Recurse -File -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -notmatch '\\(_Private|\.git|graphify-out|node_modules|\.venv)\\' }

$bytes  = ($md | Measure-Object -Property Length -Sum).Sum
$tokIn  = [math]::Round($bytes / 4)        # ~4 chars/token, English prose
$tokOut = [math]::Round($tokIn * 0.3)      # graphify's JSON output ~30% of input
$cost   = ($tokIn/1e6 * $PRICE_IN) + ($tokOut/1e6 * $PRICE_OUT)

Log "  files      : $($md.Count)"
Log "  size       : $([math]::Round($bytes/1MB,2)) MB"
Log "  input tok  : $('{0:N0}' -f $tokIn)"
Log "  EST. COST  : `$$([math]::Round($cost,2))" Yellow
if ($Backend -eq 'ollama') { Log "  ACTUAL     : `$0.00 (local)" Green }

# Off-peak nudge — DeepSeek has historically discounted 16:30-00:30 UTC.
if ($Backend -eq 'deepseek') {
    $u = (Get-Date).ToUniversalTime().TimeOfDay
    if (($u -ge [timespan]'16:30') -or ($u -lt [timespan]'00:30')) {
        Log "  timing     : OFF-PEAK — discount likely applies" Green
    } else {
        Log "  timing     : peak. Off-peak (16:30-00:30 UTC) is cheaper." DarkGray
    }
}

if ($DryRun) { Log "  [DRY RUN] Nothing sent. Nothing spent." Yellow; exit 0 }

# --- SPEND GUARD -----------------------------------------------------------
# $2 isn't scary. An UNEXPECTED $2 is. If the estimate blows past this, the
# corpus has something in it that shouldn't be there. Look before you pay.
if ($cost -gt 2.00 -and $Backend -eq 'deepseek') {
    Log "  ESTIMATE > `$2.00 — halting for confirmation." Red
    if ((Read-Host "  Spend ~`$$([math]::Round($cost,2))? (yes/no)") -ne 'yes') {
        Log "  Aborted by Chief." Yellow; exit 0
    }
}

Push-Location $root
try {
    $a = @('extract','.','--backend',$Backend,'--token-budget',"$TokenBudget",'--update')
    if ($Backend -eq 'ollama') { $a += @('--max-concurrency','2','--api-timeout','900') }

    Log "  graphify $($a -join ' ')" DarkGray
    & graphify @a 2>&1 | Tee-Object -Variable so | Out-Null
    if ($so -match 'chunk .* failed') { Log "  WARN: some chunks failed — partial graph." Yellow }

    & graphify cluster-only . --no-label 2>&1 | Out-Null

    # graphify's own meter. TRUST THIS over my estimate — it's measured, not modeled.
    $cf = Join-Path $root 'graphify-out\cost.json'
    if (Test-Path $cf) {
        Log "  ACTUAL COST (graphify cost.json):" Green
        Get-Content $cf | ForEach-Object { Log "    $_" Green }
    }
}
catch { Log "  PASS C FAILED: $($_.Exception.Message)" Red }
finally { Pop-Location }

# ===========================================================================
# GLOBAL — fuse everything into one cross-repo graph
# ===========================================================================
Log "--- Refreshing global graph" Cyan
foreach ($r in $REPOS) {
    $gj = Join-Path $r.path 'graphify-out\graph.json'
    if (Test-Path $gj) { & graphify global add "$gj" --as $r.alias 2>&1 | Out-Null }
}
& graphify global list 2>&1 | ForEach-Object { Log "  $_" }

Log "=== DONE ===" Green
Log "Restart Claude Desktop to pick up the refreshed graph." Cyan
