param(
  [Parameter(Mandatory=$true)]
  [string]$Candidates,

  [Parameter(Mandatory=$true)]
  [string]$OutputDir,

  [string]$Seeds,
  [int]$MinimumScore = 50,
  [int]$MaximumDrafts = 0
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InvocationDir = (Get-Location).Path
$Python = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}

$CandidatesPath = if ([System.IO.Path]::IsPathRooted($Candidates)) { $Candidates } else { Join-Path $InvocationDir $Candidates }
$OutputPath = if ([System.IO.Path]::IsPathRooted($OutputDir)) { $OutputDir } else { Join-Path $InvocationDir $OutputDir }

$ArgsList = @(
  "-m", "mention_radar.tailored_drafts",
  "--candidates", $CandidatesPath,
  "--output-dir", $OutputPath,
  "--minimum-score", "$MinimumScore"
)
if ($Seeds) {
  $SeedsPath = if ([System.IO.Path]::IsPathRooted($Seeds)) { $Seeds } else { Join-Path $InvocationDir $Seeds }
  $ArgsList += @("--seeds", $SeedsPath)
}
if ($MaximumDrafts -gt 0) {
  $ArgsList += @("--maximum-drafts", "$MaximumDrafts")
}

Push-Location $ScriptDir
try {
  & $Python @ArgsList
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}
