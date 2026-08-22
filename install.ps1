# Deep Market Research Skill - Windows one-click installer
# Detects installed agent platforms and copies the skill into their skills/ directory.

$SkillDir = "deep-market-research"
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
$Files = @("SKILL.md", "README.md", "README_EN.md", "references", "assets", "benchmarks", "scripts", "LICENSE", "CONTRIBUTING.md", ".gitignore")

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

$installed = 0
foreach ($base in $Targets) {
  if (Test-Path $base) {
    $dest = Join-Path $base $SkillDir
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
    Write-Host "Installed to $dest"
    $installed++
  }
}

if ($installed -eq 0) {
  Write-Host "No supported agent skills directory found. Manually copy this folder to your agent's skills directory."
  exit 1
}
Write-Host "Done. Restart your agent to load 'deep-market-research'."
