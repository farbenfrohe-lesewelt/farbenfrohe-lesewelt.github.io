param(
    [string]$InputCsv,
    [string]$ImportCsv,
    [string[]]$Url = @(),
    [string[]]$Feed = @(),
    [string]$FeedList,
    [string]$Config = ".\tools\mention-radar\config.example.yaml",
    [string]$OutputDir,
    [switch]$NoVenv,
    [switch]$NoDrafts,
    [switch]$NoInstall
)

$ErrorActionPreference = "Stop"
$toolRoot = Join-Path $PSScriptRoot ""
$python = "python"

$hasInput = $false
if ($InputCsv) { $hasInput = $true }
if ($ImportCsv) { $hasInput = $true }
if ($Url.Count -gt 0) { $hasInput = $true }
if ($Feed.Count -gt 0) { $hasInput = $true }
if ($FeedList) { $hasInput = $true }

if (-not $hasInput) {
    throw "Mindestens eine Eingabe ist erforderlich: -InputCsv, -ImportCsv, -Url, -Feed oder -FeedList."
}

if ($InputCsv -and -not (Test-Path $InputCsv)) {
    throw "Eingabedatei nicht gefunden: $InputCsv"
}
if ($ImportCsv -and -not (Test-Path $ImportCsv)) {
    throw "Importdatei nicht gefunden: $ImportCsv"
}
if ($FeedList -and -not (Test-Path $FeedList)) {
    throw "Feed-Liste nicht gefunden: $FeedList"
}

if (-not $NoVenv) {
    $venv = Join-Path $toolRoot ".venv"
    if (-not (Test-Path $venv)) {
        & $python -m venv $venv
    }
    $python = Join-Path $venv "Scripts\python.exe"
}

if (-not $NoInstall) {
    & $python -m pip install -r (Join-Path $toolRoot "requirements.txt")
}

$argsList = @(
    (Join-Path $toolRoot "mention_radar.py"),
    "--config", $Config
)

if ($InputCsv) {
    $argsList += @("--input-csv", $InputCsv)
}
if ($ImportCsv) {
    $argsList += @("--import-csv", $ImportCsv)
}
foreach ($item in $Url) {
    $argsList += @("--url", $item)
}
foreach ($item in $Feed) {
    $argsList += @("--feed", $item)
}
if ($FeedList) {
    $argsList += @("--feed-list", $FeedList)
}
if ($OutputDir) {
    $argsList += @("--output-dir", $OutputDir)
}
if ($NoDrafts) {
    $argsList += "--no-drafts"
}

& $python @argsList

if ($OutputDir -and (Test-Path $OutputDir)) {
    Invoke-Item $OutputDir
} else {
    $runs = ".\local-data\mention-radar\runs"
    if (Test-Path $runs) {
        Invoke-Item $runs
    }
}
