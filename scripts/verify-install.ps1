# Verifies T-800 Agent installation after install-plugin.ps1.
# Канон: артефакты внутри PLUGIN_DEST, не в ~/.cursor/{agents,commands,rules,skills}
# Usage: .\scripts\verify-install.ps1

$ErrorActionPreference = "Stop"

$plugin = Join-Path $env:USERPROFILE ".cursor\plugins\local\t-800-agent"
$agents = Join-Path $plugin "agents"
$rules = Join-Path $plugin "rules"
$cmds = Join-Path $plugin "commands"
$skills = Join-Path $plugin "skills"
$userRules = Join-Path $env:USERPROFILE ".cursor\rules"
$userAgents = Join-Path $env:USERPROFILE ".cursor\agents"
$userSkills = Join-Path $env:USERPROFILE ".cursor\skills"

$checks = @(
    @{ Name = "t-800-operator subagent"; Path = Join-Path $agents "t-800-operator.md"; ShouldExist = $true; MustContain = "name: t-800-operator" },
    @{ Name = "t-800-maintainer subagent"; Path = Join-Path $agents "t-800-maintainer.md"; ShouldExist = $true; MustContain = "name: t-800-maintainer" },
    @{ Name = "maintainer skill"; Path = Join-Path $skills "t-800-knowledge-base\SKILL.md"; ShouldExist = $true; MustContain = "disable-model-invocation: true" },
    @{ Name = "operator routing rule"; Path = Join-Path $rules "t-800-operator-routing.mdc"; ShouldExist = $true; MustContain = "Task(t-800-operator)" },
    @{ Name = "knowledge refresh rule"; Path = Join-Path $rules "t-800-knowledge-refresh.mdc"; ShouldExist = $true; MustContain = "sync-docs" },
    @{ Name = "t-800-operator command"; Path = Join-Path $cmds "t-800-operator.md"; ShouldExist = $true; MustContain = "Task(t-800-operator)" },
    @{ Name = "t-800-sync command"; Path = Join-Path $cmds "t-800-sync.md"; ShouldExist = $true; MustContain = "sync-docs" },
    @{ Name = "t-800-maintain command"; Path = Join-Path $cmds "t-800-maintain.md"; ShouldExist = $true; MustContain = "Task(t-800-maintainer)" },
    @{ Name = "t-800-health command"; Path = Join-Path $cmds "t-800-health.md"; ShouldExist = $true; MustContain = "health-check" },
    @{ Name = "t-800-factory lead"; Path = Join-Path $agents "t-800-factory.md"; ShouldExist = $true; MustContain = "name: t-800-factory" },
    @{ Name = "factory routing rule"; Path = Join-Path $rules "t-800-factory-routing.mdc"; ShouldExist = $true; MustContain = "Task(t-800-factory)" },
    @{ Name = "t800-bootstrap command"; Path = Join-Path $cmds "t800-bootstrap.md"; ShouldExist = $true; MustContain = "install-global-routing-rule" },
    @{ Name = "t-800-scout"; Path = Join-Path $agents "t-800-scout.md"; ShouldExist = $true; MustContain = "name: t-800-scout" },
    @{ Name = "t-800-brain-lead"; Path = Join-Path $agents "t-800-brain-lead.md"; ShouldExist = $true; MustContain = "name: t-800-brain-lead" },
    @{ Name = "t800-start command"; Path = Join-Path $cmds "t800-start.md"; ShouldExist = $true; MustContain = "Task(t-800-scout)" },
    @{ Name = "t800-onboard command"; Path = Join-Path $cmds "t800-onboard.md"; ShouldExist = $true; MustContain = "Task(t-800-onboard)" },
    @{ Name = "t800-audit command"; Path = Join-Path $cmds "t800-audit.md"; ShouldExist = $true; MustContain = "Task(t-800-system-auditor)" },
    @{ Name = "t800-plugin-audit command"; Path = Join-Path $cmds "t800-plugin-audit.md"; ShouldExist = $true; MustContain = "Task(t-800-plugin-auditor)" },
    @{ Name = "t800-fix command"; Path = Join-Path $cmds "t800-fix.md"; ShouldExist = $true; MustContain = "t800_run_gate.py" },
    @{ Name = "t800-doctor command"; Path = Join-Path $cmds "t800-doctor.md"; ShouldExist = $true; MustContain = "t800_doctor.py" },
    @{ Name = "t800-loop command"; Path = Join-Path $cmds "t800-loop.md"; ShouldExist = $true; MustContain = "t-800-loop-conductor" },
    @{ Name = "t800-update command"; Path = Join-Path $cmds "t800-update.md"; ShouldExist = $true; MustContain = "install-plugin.sh" },
    @{ Name = "t-800-system-auditor"; Path = Join-Path $agents "t-800-system-auditor.md"; ShouldExist = $true; MustContain = "name: t-800-system-auditor" },
    @{ Name = "t-800-plugin-auditor"; Path = Join-Path $agents "t-800-plugin-auditor.md"; ShouldExist = $true; MustContain = "name: t-800-plugin-auditor" },
    @{ Name = "t-800-loop-conductor"; Path = Join-Path $agents "t-800-loop-conductor.md"; ShouldExist = $true; MustContain = "name: t-800-loop-conductor" },
    @{ Name = "t800_plugin_audit.py"; Path = Join-Path $plugin "scripts\t800_plugin_audit.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "plugin-audit-contract.md"; Path = Join-Path $plugin "shared\plugin-audit-contract.md"; ShouldExist = $true; MustContain = $null },
    @{ Name = "loop-engineering-contract.md"; Path = Join-Path $plugin "shared\loop-engineering-contract.md"; ShouldExist = $true; MustContain = $null },
    @{ Name = "lesson-schema-contract.md"; Path = Join-Path $plugin "shared\lesson-schema-contract.md"; ShouldExist = $true; MustContain = $null },
    @{ Name = "STATE.md.template"; Path = Join-Path $plugin "templates\STATE.md.template"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_loop_state.sh"; Path = Join-Path $plugin "scripts\t800_loop_state.sh"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_run_report.py"; Path = Join-Path $plugin "scripts\t800_run_report.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_lessons_export.py"; Path = Join-Path $plugin "scripts\t800_lessons_export.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_telemetry.py"; Path = Join-Path $plugin "scripts\t800_telemetry.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_risk_classifier.py"; Path = Join-Path $plugin "scripts\t800_risk_classifier.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_lessons_to_fixpack.py"; Path = Join-Path $plugin "scripts\t800_lessons_to_fixpack.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_golden_check.py"; Path = Join-Path $plugin "scripts\t800_golden_check.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800-loop-dispatcher.sh"; Path = Join-Path $plugin "scripts\t800-loop-dispatcher.sh"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t800_loop_queue_write.py"; Path = Join-Path $plugin "scripts\t800_loop_queue_write.py"; ShouldExist = $true; MustContain = $null },
    @{ Name = "t-800 legacy alias"; Path = Join-Path $cmds "t-800.md"; ShouldExist = $true; MustContain = "/t800-start" },
    @{ Name = "legacy forge command absent"; Path = Join-Path $cmds "forge.md"; ShouldExist = $false; MustContain = $null },
    @{ Name = "local plugin"; Path = Join-Path $plugin ".cursor-plugin\plugin.json"; ShouldExist = $true; MustContain = "t-800-agent" }
)

$failed = 0
$warned = 0

foreach ($check in $checks) {
    $exists = Test-Path $check.Path

    if ($check.ShouldExist -and -not $exists) {
        Write-Host "FAIL $($check.Name): missing $($check.Path)" -ForegroundColor Red
        $failed++
        continue
    }

    if (-not $check.ShouldExist -and $exists) {
        Write-Host "FAIL $($check.Name): should not exist $($check.Path)" -ForegroundColor Red
        $failed++
        continue
    }

    if ($check.ShouldExist -and $check.MustContain) {
        $content = Get-Content -LiteralPath $check.Path -Raw -Encoding utf8
        if ($content -notlike "*$($check.MustContain)*") {
            Write-Host "FAIL $($check.Name): missing marker '$($check.MustContain)'" -ForegroundColor Red
            $failed++
            continue
        }
    }

    Write-Host "OK   $($check.Name)" -ForegroundColor Green
}

$pluginJsonPath = Join-Path $plugin ".cursor-plugin\plugin.json"
$pluginJsonObj = Get-Content -LiteralPath $pluginJsonPath -Raw -Encoding utf8 | ConvertFrom-Json
$actualVer = $pluginJsonObj.version
if ([string]::IsNullOrWhiteSpace($actualVer)) {
    Write-Host "FAIL plugin.json version unreadable" -ForegroundColor Red
    $failed++
}
else {
    Write-Host "OK   plugin.json version $actualVer" -ForegroundColor Green
}

$agentContent = Get-Content -LiteralPath (Join-Path $agents "t-800-operator.md") -Raw -Encoding utf8
if ($agentContent -notlike "*readonly: true*") {
    Write-Host "FAIL t-800-operator must stay readonly" -ForegroundColor Red
    $failed++
}
else {
    Write-Host "OK   t-800-operator readonly" -ForegroundColor Green
}

$maintainerContent = Get-Content -LiteralPath (Join-Path $agents "t-800-maintainer.md") -Raw -Encoding utf8
if ($maintainerContent -notlike "*readonly: false*") {
    Write-Host "FAIL t-800-maintainer must be writable" -ForegroundColor Red
    $failed++
}
else {
    Write-Host "OK   t-800-maintainer writable" -ForegroundColor Green
}

$mandatory = Join-Path $userRules "t-800-mandatory-routing.mdc"
if (-not (Test-Path $mandatory)) {
    Write-Host "WARN global mandatory-routing rule: отсутствует — установите через /t800-bootstrap" -ForegroundColor Yellow
    $warned++
}
else {
    Write-Host "OK   global mandatory-routing rule" -ForegroundColor Green
}

$stale = $false
if (Test-Path $userAgents) {
    $staleAgents = Get-ChildItem -Path $userAgents -Filter "t-800-*.md" -File -ErrorAction SilentlyContinue
    if ($staleAgents) {
        Write-Host "WARN stale user-home agents: перезапустите install-plugin.ps1" -ForegroundColor Yellow
        $warned++
        $stale = $true
    }
}
$staleSkill = Join-Path $userSkills "t-800-knowledge-base"
if (Test-Path $staleSkill) {
    Write-Host "WARN stale user-home skill t-800-knowledge-base: перезапустите install-plugin.ps1" -ForegroundColor Yellow
    $warned++
    $stale = $true
}
if (-not $stale) {
    Write-Host "OK   no stale user-home t-800 mirrors" -ForegroundColor Green
}

if ($failed -gt 0) {
    throw "T-800 Agent verification failed: $failed problem(s). Run .\scripts\install-plugin.ps1 and restart Cursor."
}

Write-Host "T-800 Agent verification passed (warnings: $warned). Restart Cursor if you just installed it." -ForegroundColor Green
