# Audits registry/agents-registry.json against agents/ files and graph symmetry
# Usage: .\scripts\audit-agent-graph.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$registryPath = Join-Path $root "registry\agents-registry.json"
$agentsDir = Join-Path $root "agents"

if (-not (Test-Path $registryPath)) {
    throw "Registry not found: $registryPath"
}

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding utf8 | ConvertFrom-Json
$failed = 0
$agentIds = @{}

foreach ($entry in $registry.agents) {
    $agentIds[$entry.id] = $entry

    $filePath = Join-Path $root ($entry.file -replace '/', '\')
    if (-not (Test-Path $filePath)) {
        Write-Host "FAIL Registry file missing: $($entry.id) -> $($entry.file)" -ForegroundColor Red
        $failed++
        continue
    }
    Write-Host "OK   file exists: $($entry.id)" -ForegroundColor Green
}

# Orphan agent files not in registry
Get-ChildItem -Path $agentsDir -Filter "*.md" -File | ForEach-Object {
    if ($_.Name -notlike "t-800-*.md") { return }
    $id = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    if (-not $agentIds.ContainsKey($id)) {
        Write-Host "WARN Agent file not in registry: $id" -ForegroundColor Yellow
    }
}

# Graph symmetry
foreach ($entry in $registry.agents) {
    foreach ($called in @($entry.calls)) {
        if (-not $agentIds.ContainsKey($called)) {
            Write-Host "FAIL $($entry.id).calls -> unknown '$called'" -ForegroundColor Red
            $failed++
            continue
        }
        $target = $agentIds[$called]
        if (@($target.calledBy) -notcontains $entry.id) {
            Write-Host "FAIL Asymmetric: $($entry.id) calls $called but $called.calledBy lacks $($entry.id)" -ForegroundColor Red
            $failed++
        }
    }

    foreach ($caller in @($entry.calledBy)) {
        if ($caller -eq "main-agent") { continue }
        if (-not $agentIds.ContainsKey($caller)) {
            Write-Host "FAIL $($entry.id).calledBy -> unknown '$caller'" -ForegroundColor Red
            $failed++
            continue
        }
        $source = $agentIds[$caller]
        if (@($source.calls) -notcontains $entry.id) {
            Write-Host "FAIL Asymmetric: $caller should call $($entry.id)" -ForegroundColor Red
            $failed++
        }
    }
}

if ($failed -gt 0) {
    throw "Agent graph audit failed: $failed problem(s)."
}

Write-Host "Agent graph audit passed ($($registry.agents.Count) registry entries)." -ForegroundColor Green
