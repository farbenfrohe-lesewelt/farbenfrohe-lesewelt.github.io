param(
    [Parameter(Mandatory = $true)]
    [string]$InputCsv,

    [string]$Config = ".\tools\mention-radar\config.example.yaml",
    [string]$OutputDir = ".\local-data\mention-radar",
    [switch]$NoVenv,
    [switch]$NoDrafts
)

$ErrorActionPreference = "Stop"
$toolRoot = Join-Path $PSScriptRoot ""
$python = "python"

if (-not (Test-Path $InputCsv)) {
    throw "Eingabedatei nicht gefunden: $InputCsv"
}

if (-not $NoVenv) {
    $venv = Join-Path $toolRoot ".venv"
    if (-not (Test-Path $venv)) {
        & $python -m venv $venv
    }
    $python = Join-Path $venv "Scripts\python.exe"
}

& $python -m pip install -r (Join-Path $toolRoot "requirements.txt")

$argsList = @(
    (Join-Path $toolRoot "mention_radar.py"),
    "--config", $Config,
    "--input-csv", $InputCsv,
    "--output-dir", $OutputDir
)

if ($NoDrafts) {
    $argsList += "--no-drafts"
}

& $python @argsList

if (Test-Path $OutputDir) {
    Invoke-Item $OutputDir
}
