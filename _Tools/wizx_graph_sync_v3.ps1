<#
.SYNOPSIS
    WIZX Graph Sync v3 - the jobs graphify does NOT do for itself.

.DESCRIPTION
    North Star: one graph spanning every repo + the DB schema + the vault,
    never stale, for under $2/month total.

    Author: wiz-9   Revised: 2026-07-11
    ASCII-ONLY BY DESIGN. PowerShell 5.1 reads .ps1 as Windows-1252 unless a BOM
    is present. Any non-ASCII char in here (dashes, glyphs, math symbols) gets
    mangled and the parser explodes with misleading cascade errors. Do not add
    fancy characters to this file. Ever.

    WHAT THIS SCRIPT IS *NOT* FOR
    -----------------------------
    Keeping the CODE graph fresh is NOT this script's job. Graphify does that
    itself, better, for free:

        graphify hook install     # git post-commit -> graph rebuilds. AST only.

    Event-driven beats a cron. Run this once with -InstallHooks and then stop
    thinking about the code graph forever.

    This script exists for the three things graphify cannot do alone:
      1. Dump XMotion.db SCHEMA to .sql so it can be graphed at all.
         (graphify skips binary .db files entirely - "not classified")
      2. Run the PAID vault pass with a cost ESTIMATE and a SPEND GUARD in front.
         (left alone, graphify finds DEEPSEEK_API_KEY in your env and just spends)
      3. Re-register the global cross-repo graph. (not automatic)

    COST
    ----
      PASS A  code (--update)   AST, local           $0.00  always
      PASS B  schema dump       sqlite3 .schema      $0.00  always
      PASS C  vault semantic    DeepSeek V4-Flash   ~$0.30  first run only
                                                    ~$0.00  after (cached)

    Pass C requires -Semantic. You ask for it, every time. No exceptions.

.EXAMPLE
    .\wizx_graph_sync_v3.ps1 -InstallHooks       # ONCE. Code then stays fresh, free.
    .\wizx_graph_sync_v3.ps1                     # code + schema. $0.00.
    .\wizx_graph_sync_v3.ps1 -Semantic -DryRun   # estimate vault. Spends nothing.
    .\wizx_graph_sync_v3.ps1 -Semantic           # ingest vault. ~$0.30.
#>

[CmdletBinding()]
param(
    [switch]$InstallHooks,
    [switch]$Semantic,
    [switch]$DryRun,
    [ValidateSet('deepseek','ollama')]
    [string]$Backend = 'deepseek',
    [int]$TokenBudget = 8000
)

$ErrorActionPreference = 'Continue'

# ---------------------------------------------------------------------------
# REPOS
#   code_only = pure code. Pass A only. Always free.
#   hybrid    = code AND vault markdown. Pass A skipped, handled in Pass C.
#
# DELIBERATELY ABSENT: C:\dev\nautilus_trader-develop (framework root).
# That is a vendor library you consume, not code you own. Graphing it would bury
# your own nodes under tens of thousands of Nautilus internals.
# ---------------------------------------------------------------------------
$REPOS = @(
    @{ alias='trading';     path='C:\dev\nautilus_trader-develop\dashboard'; kind='code_only' }
    @{ alias='ai_strategy'; path='C:\dev\ai_strategy';                       kind='code_only' }
    @{ alias='binura';      path='C:\dev\Binura';                            kind='code_only' }
    @{ alias='fibonacci';   path='C:\dev\fibonacci_strategy';                kind='code_only' }
    @{ alias='xmotion';     path='C:\dev\XMotion';                           kind='hybrid'    }
)

$XMOTION_DB = 'C:\dev\XMotion\XMotion.db'
$SCHEMA_DIR = 'C:\dev\XMotion\_schema'
$SCHEMA_SQL = 'C:\dev\XMotion\_schema\xmotion_schema.sql'
$LOG        = 'C:\dev\XMotion\_Handoffs\graph_sync.log'

# DeepSeek V4-Flash, per 1M tokens, as of 2026-07-11. Re-verify before trusting.
$PRICE_IN  = 0.14
$PRICE_OUT = 0.28

# Ignore patterns. Written BEFORE any build, every run. This is the cost shield.
$IGNORE_CODE = @(
    '*.md','*.mdx','*.txt','*.rst','*.pdf','*.yaml','*.yml','*.html','*.ndjson',
    '*.png','*.jpg','*.jpeg','*.webp','*.gif','*.svg','*.ico','*.mp3','*.wav',
    '*.mp4','*.mov','*.ttf','*.woff','*.woff2',
    '*.mq5','*.mqh',
    'node_modules/','dist/','target/','.venv/','__pycache__/','.vercel/'
)

# XMotion is hybrid - markdown is the POINT there, so it is NOT ignored.
# Media and private credentials absolutely are.
$IGNORE_HYBRID = @(
    '*.png','*.jpg','*.jpeg','*.webp','*.gif','*.svg','*.ico',
    '*.mp4','*.mov','*.mp3','*.wav','*.ttf',
    '_Private/','node_modules/','.venv/','__pycache__/'
)

New-Item -ItemType Directory -Force -Path (Split-Path $LOG) | Out-Null

function Log {
    param($m, $c = 'White')
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $line -ForegroundColor $c
    Add-Content -Path $LOG -Value $line
}

Log "=== WIZX GRAPH SYNC v3 ===" Magenta
if ($DryRun)        { Log "DRY RUN - nothing sent, nothing spent." Yellow }
if (-not $Semantic) { Log "Code + schema only. Cost: 0.00 USD." Cyan }

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
    Log "FATAL: graphify not on PATH. Open a NEW shell, or run: uv tool update-shell" Red
    exit 1
}

function Ensure-Ignore {
    param($repo, $patterns)

    # .claudeignore - stops graphify output from nuking Claude Code's prompt
    # cache and forcing a paid full re-upload. Cheap insurance.
    $ci = Join-Path $repo '.claudeignore'
    $have = @()
    if (Test-Path $ci) { $have = Get-Content $ci }
    foreach ($p in @('graph.json', 'graphify-out/')) {
        if ($have -notcontains $p) { Add-Content -Path $ci -Value $p }
    }

    # .graphifyignore - the actual cost shield. Nothing here reaches a paid pass.
    $gi = Join-Path $repo '.graphifyignore'
    $have = @()
    if (Test-Path $gi) { $have = Get-Content $gi }
    $added = 0
    foreach ($p in $patterns) {
        if ($have -notcontains $p) { Add-Content -Path $gi -Value $p; $added++ }
    }
    return $added
}

# ===========================================================================
# HOOKS - run once. Then the code graph maintains ITSELF, free, on every commit.
# ===========================================================================
if ($InstallHooks) {
    Log "--- Installing git post-commit hooks (AST only, no API cost)" Cyan

    foreach ($r in $REPOS) {
        if (-not (Test-Path $r.path)) {
            Log ("  skip " + $r.alias + " - path missing") Yellow
            continue
        }
        if (-not (Test-Path (Join-Path $r.path '.git'))) {
            Log ("  skip " + $r.alias + " - not a git repo, hook needs one") Yellow
            continue
        }

        Push-Location $r.path
        try {
            $pat = $IGNORE_CODE
            if ($r.kind -eq 'hybrid') { $pat = $IGNORE_HYBRID }

            # Shield goes up BEFORE the hook can ever fire.
            Ensure-Ignore $r.path $pat | Out-Null

            & graphify hook install 2>&1 | Out-Null
            Log ("  " + $r.alias + ": hook installed") Green
        }
        catch { Log ("  " + $r.alias + " hook FAILED: " + $_.Exception.Message) Red }
        finally { Pop-Location }
    }

    Log "Code graphs now self-update on every git commit. Free." Green
    Log "NOTE: hooks are AST-only per graphify docs. Watch the log anyway." DarkGray
}

# ===========================================================================
# PASS A - CODE. Local AST. Free. Always.
# ===========================================================================
Log "--- PASS A: code (AST, local, 0.00 USD)" Cyan

foreach ($r in $REPOS) {
    if (-not (Test-Path $r.path)) {
        Log ("  skip " + $r.alias + " - path missing") Yellow
        continue
    }

    Push-Location $r.path
    try {
        $pat = $IGNORE_CODE
        if ($r.kind -eq 'hybrid') { $pat = $IGNORE_HYBRID }

        $n = Ensure-Ignore $r.path $pat
        if ($n -gt 0) { Log ("  " + $r.alias + ": +" + $n + " ignore rules") DarkGray }

        # For the hybrid repo we do NOT run the plain code pass. Its markdown is
        # IN SCOPE, so `graphify .` here would fire an UNGUARDED paid semantic
        # pass. It belongs to Pass C, where the estimate and spend guard live.
        if ($r.kind -eq 'hybrid') {
            Log ("  " + $r.alias + ": deferred to Pass C (hybrid repo)") DarkGray
            Pop-Location
            continue
        }

        $out = & graphify . --update 2>&1 | Out-String

        # TRIPWIRE. A semantic pass must NEVER fire in the code pass. If it does,
        # an ignore rule has a hole and you are being billed for it, silently.
        if ($out -match 'semantic extraction') {
            Log ("  !! " + $r.alias + ": SEMANTIC PASS FIRED DURING CODE PASS.") Red
            Log "  !! .graphifyignore has a hole. THIS COSTS MONEY. Investigate." Red
        }

        if ($out -match 'graph\.json: (\d+) nodes, (\d+) edges') {
            Log ("  " + $r.alias + ": " + $Matches[1] + " nodes / " + $Matches[2] + " edges") Green
        }
        else {
            Log ("  " + $r.alias + ": unchanged") DarkGray
        }

        & graphify cluster-only . --no-label 2>&1 | Out-Null
    }
    catch { Log ("  " + $r.alias + " FAILED: " + $_.Exception.Message) Red }
    finally {
        if ((Get-Location).Path -eq $r.path) { Pop-Location }
    }
}

# ===========================================================================
# PASS B - DB SCHEMA. Free.
#
# graphify CANNOT read XMotion.db. A .db is a binary blob; it gets skipped as
# "not classified", same as a .ttf font. But graphify CAN read .sql as text.
#
# .schema emits DDL ONLY - CREATE TABLE, columns, FKs, view definitions.
# ZERO ROWS. No listings, no addresses, no client data, no scores. Just shape.
#
# Payoff: your 8 tables + 8 views become graph nodes, wired to the Python that
# reads and writes them. That is the code-to-schema join. It is the whole point.
# ===========================================================================
Log "--- PASS B: DB schema (0.00 USD)" Cyan

if (Test-Path $XMOTION_DB) {
    if (Get-Command sqlite3 -ErrorAction SilentlyContinue) {
        New-Item -ItemType Directory -Force -Path $SCHEMA_DIR | Out-Null
        if ($DryRun) {
            Log ("  [dry] would dump schema -> " + $SCHEMA_SQL) DarkGray
        }
        else {
            & sqlite3 $XMOTION_DB ".schema" | Set-Content -Path $SCHEMA_SQL -Encoding UTF8
            $lines = (Get-Content $SCHEMA_SQL | Measure-Object -Line).Lines
            Log ("  schema: " + $lines + " lines -> " + $SCHEMA_SQL) Green
        }
    }
    else {
        Log "  sqlite3 not found. Install: winget install SQLite.SQLite" Yellow
        Log "  (Pass B is a nice-to-have. Everything else still works.)" DarkGray
    }
}
else {
    Log ("  XMotion.db not found at " + $XMOTION_DB + " - skipping") Yellow
}

# ===========================================================================
# GLOBAL GRAPH refresh - factored out so both exit paths use it.
# ===========================================================================
function Refresh-Global {
    Log "--- Refreshing global graph" Cyan
    foreach ($r in $REPOS) {
        $gj = Join-Path $r.path 'graphify-out\graph.json'
        if (Test-Path $gj) {
            & graphify global add "$gj" --as $r.alias 2>&1 | Out-Null
        }
    }
    & graphify global list 2>&1 | ForEach-Object { Log ("  " + $_) }
}

# ===========================================================================
# PASS C - VAULT SEMANTIC. THE ONLY PASS THAT SPENDS MONEY.
# ===========================================================================
if (-not $Semantic) {
    Log "--- PASS C: SKIPPED (no -Semantic flag)" DarkGray
    Refresh-Global
    Log "=== DONE. Spend this run: 0.00 USD ===" Green
    exit 0
}

$hybrid = $REPOS | Where-Object { $_.kind -eq 'hybrid' } | Select-Object -First 1
$root = $hybrid.path

Log ("--- PASS C: vault semantic [" + $hybrid.alias + "] [backend: " + $Backend + "]") Yellow

if (-not (Test-Path $root)) {
    Log ("  " + $root + " missing. Abort.") Red
    exit 1
}

# --- ESTIMATE BEFORE SPENDING. NON-NEGOTIABLE. -----------------------------
$md = Get-ChildItem -Path $root -Include *.md,*.txt,*.sql -Recurse -File -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -notmatch '\\(_Private|\.git|graphify-out|node_modules|\.venv)\\' }

$bytes = 0
if ($md) { $bytes = ($md | Measure-Object -Property Length -Sum).Sum }

$tokIn  = [math]::Round($bytes / 4)      # ~4 chars per token, English prose
$tokOut = [math]::Round($tokIn * 0.3)    # graphify JSON output ~30% of input
$cost   = ($tokIn / 1000000 * $PRICE_IN) + ($tokOut / 1000000 * $PRICE_OUT)
$costR  = [math]::Round($cost, 2)

$fileCount = 0
if ($md) { $fileCount = $md.Count }

Log ("  files      : " + $fileCount)
Log ("  size       : " + [math]::Round($bytes / 1MB, 2) + " MB")
Log ("  input tok  : " + ('{0:N0}' -f $tokIn))
Log ("  EST. COST  : " + $costR + " USD") Yellow

if ($Backend -eq 'ollama') { Log "  ACTUAL     : 0.00 USD (local model)" Green }

# Off-peak nudge. DeepSeek has historically discounted 16:30-00:30 UTC.
if ($Backend -eq 'deepseek') {
    $u = (Get-Date).ToUniversalTime().TimeOfDay
    if (($u -ge [timespan]'16:30') -or ($u -lt [timespan]'00:30')) {
        Log "  timing     : OFF-PEAK window - discount likely applies" Green
    }
    else {
        Log "  timing     : peak hours. Off-peak 16:30-00:30 UTC is cheaper." DarkGray
    }
}

if ($DryRun) {
    Log "  [DRY RUN] Nothing sent. Nothing spent." Yellow
    Log "=== DONE (dry) ===" Green
    exit 0
}

# --- SPEND GUARD -----------------------------------------------------------
# 2 USD is not a scary number. An UNEXPECTED 2 USD is. If the estimate blows
# past this, the corpus contains something it should not. Look before you pay.
if ($cost -gt 2.00 -and $Backend -eq 'deepseek') {
    Log ("  ESTIMATE OVER 2.00 USD - halting for confirmation.") Red
    $ans = Read-Host ("  Proceed and spend about " + $costR + " USD? (yes/no)")
    if ($ans -ne 'yes') {
        Log "  Aborted by Chief." Yellow
        exit 0
    }
}

Push-Location $root
try {
    $cmdArgs = @('extract', '.', '--backend', $Backend, '--token-budget', "$TokenBudget", '--update')
    if ($Backend -eq 'ollama') {
        $cmdArgs += @('--max-concurrency', '2', '--api-timeout', '900')
    }

    Log ("  graphify " + ($cmdArgs -join ' ')) DarkGray

    $semOut = & graphify @cmdArgs 2>&1 | Out-String
    Write-Host $semOut

    if ($semOut -match 'chunk .* failed') {
        Log "  WARNING: some chunks failed - partial graph. See output above." Yellow
    }

    & graphify cluster-only . --no-label 2>&1 | Out-Null

    # graphify's own meter. TRUST THIS over my estimate - measured, not modeled.
    $cf = Join-Path $root 'graphify-out\cost.json'
    if (Test-Path $cf) {
        Log "  ACTUAL COST (graphify cost.json):" Green
        Get-Content $cf | ForEach-Object { Log ("    " + $_) Green }
    }
    else {
        Log "  (no cost.json written - check your DeepSeek dashboard)" DarkGray
    }
}
catch { Log ("  PASS C FAILED: " + $_.Exception.Message) Red }
finally { Pop-Location }

Refresh-Global

Log "=== DONE ===" Green
Log "Restart Claude Desktop to pick up the refreshed graph." Cyan
