# Validates all subagent files in agents/
# Usage: .\scripts\validate-agents.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$agentsDir = Join-Path $root "agents"

$failed = 0
$checked = 0

Get-ChildItem -Path $agentsDir -Filter "*.md" -File | ForEach-Object {
    if ($_.Name -notlike "t-800-*.md") { return }

    $checked++
    $content = Get-Content -LiteralPath $_.FullName -Raw -Encoding utf8
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)

    if ($content -notmatch '(?m)^---\s*$') {
        Write-Host "FAIL $($_.Name): missing YAML frontmatter" -ForegroundColor Red
        $failed++
        return
    }

    if ($content -notmatch 'name:\s*([a-z0-9-]+)') {
        Write-Host "FAIL $($_.Name): missing or invalid name in frontmatter" -ForegroundColor Red
        $failed++
        return
    }

    $name = $Matches[1]
    if ($name -ne $baseName) {
        Write-Host "FAIL $($_.Name): name '$name' does not match filename '$baseName'" -ForegroundColor Red
        $failed++
    }

    if ($content -notmatch 'description:') {
        Write-Host "FAIL $($_.Name): missing description" -ForegroundColor Red
        $failed++
    }

    if ($content -match 'description:.*helps with (tasks|code|things)' -or
        $content -match 'description:.*general') {
        Write-Host "WARN $($_.Name): vague description detected" -ForegroundColor Yellow
    }

    $lineCount = ($content -split "`n").Count
    if ($lineCount -gt 200) {
        Write-Host "WARN $($_.Name): prompt is long ($lineCount lines)" -ForegroundColor Yellow
    }

    Write-Host "OK   $($_.Name) ($name)" -ForegroundColor Green
}

if ($checked -eq 0) {
    throw "No agent files found in $agentsDir"
}

if ($failed -gt 0) {
    throw "Agent validation failed: $failed problem(s)."
}

Write-Host "Agent validation passed ($checked agents)." -ForegroundColor Green
