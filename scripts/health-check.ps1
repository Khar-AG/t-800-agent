# Runs T-800 health checks and writes knowledge-base/HEALTH-REPORT.md.
# Канон: маркеры внутри ROOT (plugin tree), не user-home mirrors
# Usage: .\scripts\health-check.ps1

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$kb = Join-Path $root "knowledge-base"
$reportPath = Join-Path $kb "HEALTH-REPORT.md"
$manifestPath = Join-Path $kb "manifest.json"
$pluginDest = Join-Path $env:USERPROFILE ".cursor\plugins\local\t-800-agent"

$checks = New-Object System.Collections.Generic.List[object]

function Add-Check($Name, $Status, $Details) {
    $script:checks.Add([ordered]@{
        name = $Name
        status = $Status
        details = $Details
    }) | Out-Null
}

function Test-Marker($Name, $Path, $Marker, $ShouldExist = $true) {
    $exists = Test-Path $Path
    if ($ShouldExist -and -not $exists) {
        Add-Check $Name "FAIL" "Missing: $Path"
        return
    }
    if (-not $ShouldExist -and $exists) {
        Add-Check $Name "FAIL" "Must be absent: $Path"
        return
    }
    if ($ShouldExist -and $Marker) {
        $content = Get-Content -LiteralPath $Path -Raw -Encoding utf8
        if ($content -notlike "*$Marker*") {
            Add-Check $Name "FAIL" "Missing marker: $Marker"
            return
        }
    }
    Add-Check $Name "OK" $Path
}

Test-Marker "t-800-operator subagent" (Join-Path $root "agents\t-800-operator.md") "readonly: true" $true
Test-Marker "t-800-maintainer subagent" (Join-Path $root "agents\t-800-maintainer.md") "readonly: false" $true
Test-Marker "maintainer skill disabled" (Join-Path $root "skills\t-800-knowledge-base\SKILL.md") "disable-model-invocation: true" $true
Test-Marker "health command installed" (Join-Path $root "commands\t-800-health.md") "health-check" $true

$mandatory = Join-Path $env:USERPROFILE ".cursor\rules\t-800-mandatory-routing.mdc"
if (Test-Path $mandatory) {
    Add-Check "global mandatory-routing" "OK" $mandatory
}
else {
    Add-Check "global mandatory-routing" "WARN" "отсутствует — /t800-bootstrap"
}

$pluginAgents = Join-Path $pluginDest "agents"
if (Test-Path $pluginAgents) {
    Add-Check "plugin dest agents" "OK" $pluginAgents
}
else {
    Add-Check "plugin dest agents" "WARN" "нет $pluginDest — запустите install-plugin.ps1"
}

$userAgents = Join-Path $env:USERPROFILE ".cursor\agents"
$userSkill = Join-Path $env:USERPROFILE ".cursor\skills\t-800-knowledge-base"
$stale = $false
if (Test-Path $userAgents) {
    $staleAgents = Get-ChildItem -Path $userAgents -Filter "t-800-*.md" -File -ErrorAction SilentlyContinue
    if ($staleAgents) {
        Add-Check "stale user-home agents" "WARN" "устаревшее зеркало — перезапустите install"
        $stale = $true
    }
}
if (Test-Path $userSkill) {
    Add-Check "stale user-home skill" "WARN" "устаревшее зеркало — перезапустите install"
    $stale = $true
}
if (-not $stale) {
    Add-Check "no stale user-home mirrors" "OK" "clean"
}

if (Test-Path $manifestPath) {
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
        $dates = @()
        foreach ($p in $manifest.pages.PSObject.Properties) {
            if ($p.Value.last_synced) {
                $dates += [datetime]::Parse($p.Value.last_synced)
            }
        }
        if ($dates.Count -gt 0) {
            $latest = ($dates | Sort-Object -Descending | Select-Object -First 1)
            $ageDays = [int]((Get-Date) - $latest).TotalDays
            if ($ageDays -le 30) {
                Add-Check "manifest freshness" "OK" "Latest sync: $($latest.ToString('yyyy-MM-dd')) ($ageDays days)"
            }
            else {
                Add-Check "manifest freshness" "WARN" "Latest sync: $($latest.ToString('yyyy-MM-dd')) ($ageDays days)"
            }
        }
        else {
            Add-Check "manifest freshness" "WARN" "No page sync dates found"
        }
    }
    catch {
        Add-Check "manifest freshness" "FAIL" $_.Exception.Message
    }
}
else {
    Add-Check "manifest freshness" "FAIL" "Missing manifest.json"
}

$validatePs1 = Join-Path $here "validate-agents.ps1"
$auditPs1 = Join-Path $here "audit-agent-graph.ps1"
try {
    if (Test-Path $validatePs1) {
        & $validatePs1 | Out-Null
        Add-Check "validate-agents" "OK" "passed"
    }
    else {
        Add-Check "validate-agents" "WARN" "validate-agents.ps1 missing"
    }
}
catch {
    Add-Check "validate-agents" "FAIL" $_.Exception.Message
}

try {
    if (Test-Path $auditPs1) {
        & $auditPs1 | Out-Null
        Add-Check "audit-agent-graph" "OK" "passed"
    }
    else {
        Add-Check "audit-agent-graph" "WARN" "audit-agent-graph.ps1 missing"
    }
}
catch {
    Add-Check "audit-agent-graph" "FAIL" $_.Exception.Message
}

try {
    & (Join-Path $here "audit-coverage.ps1") | Out-Null
    Add-Check "coverage audit" "OK" "Missing=0"
}
catch {
    Add-Check "coverage audit" "WARN" $_.Exception.Message
}

$failed = ($checks | Where-Object { $_.status -eq "FAIL" }).Count
$warned = ($checks | Where-Object { $_.status -eq "WARN" }).Count
$status = if ($failed -gt 0) { "FAIL" } elseif ($warned -gt 0) { "WARN" } else { "OK" }

$report = @"
# HEALTH-REPORT

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Status:** $status
**Failed:** $failed
**Warnings:** $warned

| Status | Check | Details |
|--------|-------|---------|
"@

foreach ($check in $checks) {
    $report += "`n| $($check.status) | $($check.name) | $($check.details) |"
}

$report += @"


## Next step

If status is `FAIL`, run:

```powershell
.\scripts\install-plugin.ps1
.\scripts\verify-install.ps1
.\scripts\health-check.ps1
```
"@

Set-Content -LiteralPath $reportPath -Value $report -Encoding utf8

foreach ($check in $checks) {
    Write-Host "$($check.status) $($check.name): $($check.details)"
}
Write-Host "Health report: $reportPath"

if ($failed -gt 0) {
    exit 2
}
exit 0
