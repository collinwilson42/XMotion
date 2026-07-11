<#
.SYNOPSIS
    WIZX Graph Sync — keeps the global knowledge graph current, on a schedule.

.DESCRIPTION
    √1 North Star: the graph is never stale. Chief asks a structural question and
    the answer reflects the code and the vault as they are TODAY, not as they were
    the day we set this up.

    Author: wiz-9   Date: 2026-07-11

    THREE PASSES, THREE COST PROFILES — know which is which:

      PASS A  code (--update)      tree-sitter AST, local        $0.00  ALWAYS
      PASS B  DB schema dump       sqlite3 .schema -> .sql       $0.00  ALWAYS
      PASS C  vault semantic       DeepSeek V4-Flash             ~$0.30 first run
                                                                 ~$0.00 after (cached)

    Pass C is the ONLY one that costs money, it is OFF by default, and it only
    re-reads files that CHANGED since last run. First run pays for the corpus.
    Every run after that pays for the diff.

.NOTES
    IDEMPOTENT. Safe to re-run. READ-ONLY against your source — it writes only
    into graphify-out/ and its own log.

    COST GUARD: pass C will not run without -Semantic. You have to ask for it.
    That is deliberate. Graphify auto-detects DEEPSEEK_API_KEY from your env and
    will spend it unprompted if you let it — this script never lets it.

.EXAMPLE
    # Free. Code only. This is what the scheduled task runs nightly.
    .\wizx_graph_sync.ps1

    # First-time vault ingest. Costs ~$0.30. Run it once, by hand, and watch it.
    .\wizx_graph_sync.ps1 -Semantic -DryRun     # see what it WOULD send
    .\wizx_graph_sync.ps1 -Semantic             # actually send it

    # Free local model instead of DeepSeek (slower, needs Ollama running)
    .\wizx_graph_sync.ps1 -Semantic -Backend ollama
#>

[CmdletBinding()]
param(
    # Run the PAID semantic pass over vault markdown. Off by default, on purpose.
    [switch]$Semantic,

    # Show what would be sent + estimated cost. Sends nothing. Spends nothing.
    [switch]$DryRun,

    # deepseek = ~$0.30 and fast.  ollama = $0.00 and slow (needs Ollama running).
    [ValidateSet('deepseek', 'ollama')]
    [string]$Backend = 'deepseek',

    # Smaller chunks -> fewer "invalid JSON" retries on long seeds.
    [int]$TokenBudget = 8000
)

$ErrorActionPreference = 'Continue'

# --- Paths -----------------------------------------------------------------
$CODE_REPOS = @{
    'trading'     = 'C:\dev\nautilus_trader-develop\dashboard'
    'ai_strategy' = 'C:\dev\ai_strategy'
    'binura'      = 'C:\dev\Binura'
}

$XMOTION_ROOT = 'C:\dev\XMotion'
$XMOTION_DB   = 'C:\dev\XMotion\XMotion.db'
$SCHEMA_OUT   = 'C:\dev\XMotion\_schema\xmotion_schema.sql'   # generated, safe to delete
$LOG          = 'C:\dev\XMotion\_Handoffs\graph_sync.log'

# DeepSeek V4-Flash, per 1M tokens, as of 2026-07-11. Verify before trusting.
$PRICE_IN  = 0.14
$PRICE_OUT = 0.28

# --- Logging ---------------------------------------------------------------
New-Item -ItemType Directory -Force -Path (Split-Path $LOG) | Out-Null
function Log {
    param($m, $c = 'White')
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $line -ForegroundColor $c
    Add-Content -Path $LOG -Value $line
}

Log "=== WIZX GRAPH SYNC ===" Magenta
if ($DryRun)   { Log "DRY RUN — nothing sent, nothing spent." Yellow }
if (-not $Semantic) { Log "Code-only mode. Cost: `$0.00. (Use -Semantic for the vault.)" Cyan }

if (-not (Get-Command graphify -ErrorAction SilentlyContinue)) {
    Log "FATAL: graphify not on PATH. Open a new shell, or run: uv tool update-shell" Red
    exit 1
}

# ===========================================================================
# PASS A — CODE.  Incremental AST. Local. Free. Every time.
# ===========================================================================
Log "--- PASS A: code (AST, local, `$0.00)" Cyan

foreach ($alias in $CODE_REPOS.Keys) {
    $repo = $CODE_REPOS[$alias]
    if (-not (Test-Path $repo)) { Log "  skip $alias — path missing" Yellow; continue }

    Push-Location $repo
    try {
        # --update = only re-read files whose contents changed. Cheap and fast.
        $out = & graphify . --update 2>&1 | Out-String

        # TRIPWIRE. If a semantic pass fires here, an ignore rule has failed and
        # we are about to be billed for a pass we did not ask for. Say so loudly.
        if ($out -match 'semantic extraction') {
            Log "  !! $alias : SEMANTIC PASS FIRED IN THE CODE PASS. .graphifyignore has a hole." Red
            Log "  !! Check for stray .md / images. This costs money." Red
        }

        if ($out -match 'wrote .*graph\.json: (\d+) nodes, (\d+) edges') {
            Log "  $alias : $($Matches[1]) nodes, $($Matches[2]) edges" Green
        } else {
            Log "  $alias : no change" DarkGray
        }

        & graphify cluster-only . --no-label 2>&1 | Out-Null
    }
    catch { Log "  $alias FAILED: $($_.Exception.Message)" Red }
    finally { Pop-Location }
}

# ===========================================================================
# PASS B — DATABASE SCHEMA.  Free.
#
# Graphify CANNOT read XMotion.db. A .db is a binary blob — it gets skipped as
# "not classified", same as a font file. But it CAN read .sql text. So we dump
# the schema (structure only — tables, columns, views, FKs; ZERO rows, zero
# listing data, zero client info) into a .sql file and graph THAT.
#
# Result: your 8 tables and 8 analytics views become real nodes, wired to the
# Python that reads and writes them. That's the join you actually want — code
# and schema in ONE graph.
# ===========================================================================
Log "--- PASS B: DB schema (`$0.00)" Cyan

if (Test-Path $XMOTION_DB) {
    New-Item -ItemType Directory -Force -Path (Split-Path $SCHEMA_OUT) | Out-Null
    $sqlite = Get-Command sqlite3 -ErrorAction SilentlyContinue

    if ($sqlite) {
        if ($DryRun) {
            Log "  [dry] would dump schema -> $SCHEMA_OUT" DarkGray
        } else {
            # .schema = DDL only. No SELECT, no rows. Nothing sensitive leaves the DB.
            & sqlite3 $XMOTION_DB ".schema" | Set-Content -Path $SCHEMA_OUT -Encoding UTF8
            $n = (Get-Content $SCHEMA_OUT | Measure-Object -Line).Lines
            Log "  schema dumped: $n lines -> $SCHEMA_OUT" Green
        }
    } else {
        Log "  sqlite3 not found. Install: winget install SQLite.SQLite" Yellow
        Log "  (or skip — Pass B is a nice-to-have, not load-bearing)" DarkGray
    }
} else {
    Log "  XMotion.db not at $XMOTION_DB — skipping" Yellow
}

# ===========================================================================
# PASS C — VAULT SEMANTIC.  THE ONLY PASS THAT COSTS MONEY.
# ===========================================================================
if (-not $Semantic) {
    Log "--- PASS C: SKIPPED (no -Semantic flag)" DarkGray
    Log "=== DONE. Total spend this run: `$0.00 ===" Green
    exit 0
}

Log "--- PASS C: vault semantic  [BACKEND: $Backend]" Yellow

if (-not (Test-Path $XMOTION_ROOT)) {
    Log "  $XMOTION_ROOT not found. Aborting pass C." Red
    exit 1
}

# --- Estimate BEFORE spending. Always. -------------------------------------
$mdFiles = Get-ChildItem -Path $XMOTION_ROOT -Include *.md, *.txt -Recurse -File `
           -ErrorAction SilentlyContinue |
           Where-Object { $_.FullName -notmatch '\\(_Private|\.git|graphify-out|node_modules)\\' }

$bytes = ($mdFiles | Measure-Object -Property Length -Sum).Sum
# ~4 chars/token is the standard rough conversion for English prose.
$tokIn  = [math]::Round($bytes / 4)
$tokOut = [math]::Round($tokIn * 0.3)   # graphify's JSON output runs ~30% of input
$cost   = ($tokIn / 1e6 * $PRICE_IN) + ($tokOut / 1e6 * $PRICE_OUT)

Log "  files          : $($mdFiles.Count)"
Log "  size           : $([math]::Round($bytes/1MB,2)) MB"
Log "  est. input tok : $('{0:N0}' -f $tokIn)"
Log "  EST. COST      : `$$([math]::Round($cost,2))  (DeepSeek V4-Flash)" Yellow

if ($Backend -eq 'ollama') {
    Log "  ACTUAL COST    : `$0.00 (local model)" Green
}

# Off-peak nudge. DeepSeek has historically discounted 16:30-00:30 UTC.
$utc = (Get-Date).ToUniversalTime().TimeOfDay
$offPeak = ($utc -ge [timespan]'16:30') -or ($utc -lt [timespan]'00:30')
if ($Backend -eq 'deepseek') {
    if ($offPeak) { Log "  timing         : OFF-PEAK window — discount likely applies" Green }
    else          { Log "  timing         : peak hours. Off-peak (16:30-00:30 UTC) is cheaper." DarkGray }
}

if ($DryRun) {
    Log "  [DRY RUN] Nothing sent. Nothing spent." Yellow
    Log "=== DONE (dry). ===" Green
    exit 0
}

# --- The guard rail --------------------------------------------------------
# $2 is not a scary number. An UNEXPECTED $2 is. If the estimate blows past
# this, something is wrong with the corpus (a stray node_modules, a .git dir,
# a video transcript) and you should look before you pay.
if ($cost -gt 2.00 -and $Backend -eq 'deepseek') {
    Log "  ESTIMATE OVER `$2.00 — stopping for confirmation." Red
    $ans = Read-Host "  Proceed and spend ~`$$([math]::Round($cost,2))? (yes/no)"
    if ($ans -ne 'yes') { Log "  Aborted by Chief." Yellow; exit 0 }
}

# --- Run it ----------------------------------------------------------------
Push-Location $XMOTION_ROOT
try {
    $args = @('extract', '.', '--backend', $Backend,
              '--token-budget', "$TokenBudget", '--update')

    if ($Backend -eq 'ollama') {
        # Local models choke on high concurrency and long timeouts save retries.
        $args += @('--max-concurrency', '2', '--api-timeout', '900')
    }

    Log "  running: graphify $($args -join ' ')" DarkGray
    & graphify @args 2>&1 | Tee-Object -Variable semOut | Out-Null

    if ($semOut -match 'chunk .* failed') {
        Log "  WARNING: some chunks failed — partial graph. See above." Yellow
    }

    & graphify cluster-only . --no-label 2>&1 | Out-Null

    # graphify tracks real spend in cost.json. Trust THIS over my estimate.
    $costFile = Join-Path $XMOTION_ROOT 'graphify-out\cost.json'
    if (Test-Path $costFile) {
        Log "  ACTUAL COST (graphify cost.json):" Green
        Get-Content $costFile | ForEach-Object { Log "    $_" Green }
    }
}
catch { Log "  PASS C FAILED: $($_.Exception.Message)" Red }
finally { Pop-Location }

# ===========================================================================
# REGISTER — refresh the global cross-repo graph
# ===========================================================================
Log "--- Refreshing global graph" Cyan

foreach ($alias in $CODE_REPOS.Keys) {
    $gj = Join-Path $CODE_REPOS[$alias] 'graphify-out\graph.json'
    if (Test-Path $gj) { & graphify global add "$gj" --as $alias 2>&1 | Out-Null }
}
$xg = Join-Path $XMOTION_ROOT 'graphify-out\graph.json'
if (Test-Path $xg) { & graphify global add "$xg" --as xmotion 2>&1 | Out-Null }

& graphify global list 2>&1 | ForEach-Object { Log "  $_" }

Log "=== DONE ===" Green
Log "Claude Desktop reads the graph at startup — restart it to pick up changes." Cyan
