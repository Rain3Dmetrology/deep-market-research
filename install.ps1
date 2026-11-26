# Deep Market Research Skill - Windows one-click installer
# Detects installed agent platforms and copies the skill into their skills/ directory.

param([switch]$Check)
$ErrorActionPreference = 'Stop'
$SkillDir = "deep-market-research"
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
$Files = @("SKILL.md", "README.md", "README_EN.md", "references", "assets", "benchmarks", "scripts", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md", "sources.registry.yaml", ".gitignore")

$Targets = @(
  "$env:USERPROFILE\.claude\skills",
  "$env:USERPROFILE\.codex\skills",
  "$env:USERPROFILE\.trae\skills",
  "$env:USERPROFILE\.trae-cn\skills",
  "$env:USERPROFILE\.qoder\skills",
  "$env:USERPROFILE\.workbuddy\skills"
)

$SkillVersion = (Select-String -Path (Join-Path $Src "SKILL.md") -Pattern '^version:\s*"?([\d.]+)"?' | Select-Object -First 1).Matches.Groups[1].Value
Write-Host "Installing deep-market-research v$SkillVersion"

$Critical = @('SKILL.md','references\parameter-card-schema.md','references\run-contract.md','references\data-sources.md','scripts\evidence_contract.py','scripts\validate_param_card.py','scripts\run_contract.py','scripts\evaluate_search_benchmark.py','benchmarks\search-provider-baseline.yaml')
# Avoid relying on PowerShell module autoload in minimal or isolated hosts.
function Get-SkillHash($path) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $stream = [System.IO.File]::OpenRead($path)
  try { return [System.BitConverter]::ToString($sha.ComputeHash($stream)) }
  finally { $stream.Dispose(); $sha.Dispose() }
}
function Test-SkillCopy($dest) {
  foreach ($rel in $Critical) {
    $source = Join-Path $Src $rel
    $copy = Join-Path $dest $rel
    if (-not (Test-Path -LiteralPath $copy -PathType Leaf) -or (Get-SkillHash $source) -ne (Get-SkillHash $copy)) {
      Write-Host "FAIL: $dest/$rel missing or drifted"; return $false
    }
  }
  return $true
}
$installed = 0
$blocked = $false
foreach ($base in $Targets) {
  if (Test-Path $base) {
    $dest = Join-Path $base $SkillDir
    if ($Check) {
      if (-not (Test-SkillCopy $dest)) { $blocked = $true } else { $installed++ }
      continue
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    foreach ($f in $Files) {
      $srcPath = Join-Path $Src $f
      if (Test-Path $srcPath) {
        Copy-Item -Recurse -Force $srcPath $dest
      }
    }
    # Never ship Python bytecode caches to skill directories.
    Get-ChildItem -Path $dest -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
      Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    if (-not (Test-SkillCopy $dest)) { $blocked = $true; continue }
    Write-Host "Installed to $dest"
    $installed++
  }
}

if ($blocked) { Write-Host "RESULT: FAIL"; exit 1 }
if ($Check -and $installed -gt 0) { Write-Host "RESULT: PASS"; exit 0 }
if ($installed -eq 0) {
  Write-Host "No supported agent skills directory found. Manually copy this folder to your agent's skills directory."
  exit 1
}
Write-Host "Done. Restart your agent to load 'deep-market-research'."
