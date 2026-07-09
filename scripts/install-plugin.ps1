# Установка T-800 Agent в Cursor Desktop (Windows)
# Канон: только ~/.cursor/plugins/local/t-800-agent (без зеркал в user-home)
# Запуск: .\scripts\install-plugin.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$pluginDest = Join-Path $env:USERPROFILE ".cursor\plugins\local\t-800-agent"

Write-Host "T-800 Agent: установка..." -ForegroundColor Cyan
Write-Host "  из:  $root"
Write-Host "  в:   $pluginDest"

foreach ($legacy in @(
    (Join-Path $env:USERPROFILE ".cursor\plugins\local\cursor-forge"),
    (Join-Path $env:USERPROFILE ".cursor\plugins\local\cursor-jr"),
    (Join-Path $env:USERPROFILE ".cursor\plugins\local\t-800-operator")
)) {
    if (Test-Path $legacy) {
        Remove-Item -Path $legacy -Recurse -Force
        Write-Host "Удалён legacy: $legacy" -ForegroundColor Yellow
    }
}

if (Test-Path $pluginDest) {
    Remove-Item -Path $pluginDest -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $pluginDest | Out-Null

$exclude = @('.git', '.DS_Store', 't-800-memory')
Get-ChildItem -Path $root -Force | Where-Object {
    $exclude -notcontains $_.Name
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $pluginDest -Recurse -Force
}

$ver = (Get-Content (Join-Path $pluginDest ".cursor-plugin\plugin.json") -Raw -Encoding utf8 | ConvertFrom-Json).version

function Cleanup-StaleUserHomeMirrors {
    $agentsDir = Join-Path $env:USERPROFILE ".cursor\agents"
    $rulesDir = Join-Path $env:USERPROFILE ".cursor\rules"
    $cmdsDir = Join-Path $env:USERPROFILE ".cursor\commands"
    $skillsDir = Join-Path $env:USERPROFILE ".cursor\skills"

    if (Test-Path $agentsDir) {
        Get-ChildItem -Path $agentsDir -Filter "t-800-*.md" -File -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "  cleanup: removed $($_.FullName)"
        }
        $legacyAgents = @(
            "forge-scout", "forge-brain-lead", "forge-brain-admin", "forge-brain-agents",
            "forge-brain-cloud", "forge-brain-context", "forge-brain-dev", "forge-brain-security",
            "forge-brain-tools", "forge-factory", "forge-factory-architect", "forge-factory-auditor",
            "forge-factory-builder", "forge-factory-integrator", "cursor-jr", "cursor-jr-maintainer"
        )
        foreach ($old in $legacyAgents) {
            $p = Join-Path $agentsDir "$old.md"
            if (Test-Path $p) {
                Remove-Item $p -Force
                Write-Host "  cleanup: removed $p"
            }
        }
    }

    if (Test-Path $rulesDir) {
        Get-ChildItem -Path $rulesDir -Filter "t-800-*.mdc" -File -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.Name -eq "t-800-mandatory-routing.mdc") { return }
            Remove-Item $_.FullName -Force
            Write-Host "  cleanup: removed $($_.FullName)"
        }
        foreach ($old in @("forge-mandatory-routing", "forge-factory-routing", "cursor-jr-routing", "cursor-jr-knowledge-refresh")) {
            $p = Join-Path $rulesDir "$old.mdc"
            if (Test-Path $p) {
                Remove-Item $p -Force
                Write-Host "  cleanup: removed $p"
            }
        }
    }

    if (Test-Path $cmdsDir) {
        $cmdSrc = Join-Path $root "commands"
        if (Test-Path $cmdSrc) {
            Get-ChildItem -Path $cmdSrc -Filter "*.md" -File | ForEach-Object {
                $p = Join-Path $cmdsDir $_.Name
                if (Test-Path $p) {
                    Remove-Item $p -Force
                    Write-Host "  cleanup: removed $p"
                }
            }
        }
        foreach ($old in @("forge", "forge-factory", "forge-factory-validate", "cursor-jr", "cursor-jr-health", "cursor-jr-maintain", "cursor-jr-sync", "t800-teya")) {
            $p = Join-Path $cmdsDir "$old.md"
            if (Test-Path $p) {
                Remove-Item $p -Force
                Write-Host "  cleanup: removed $p"
            }
        }
    }

    foreach ($skill in @("t-800-knowledge-base", "cursor-jr-knowledge-base", "t-800-operator")) {
        $p = Join-Path $skillsDir $skill
        if (Test-Path $p) {
            Remove-Item -Path $p -Recurse -Force
            Write-Host "  cleanup: removed $p"
        }
    }
}

Cleanup-StaleUserHomeMirrors

# DEFER: project mirror ROOT/.cursor/agents — не блокер 1.12.1
$agentSrc = Join-Path $root "agents"
$projAgents = Join-Path $root ".cursor\agents"
if (Test-Path $agentSrc) {
    New-Item -ItemType Directory -Force -Path $projAgents | Out-Null
    Get-ChildItem -Path $agentSrc -Filter "t-800-*.md" -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $projAgents -Force
    }
}

Write-Host ""
Write-Host "Готово. T-800 Agent v$ver установлен." -ForegroundColor Green
Write-Host "Артефакты только в: $pluginDest"
Write-Host "Первый запуск: /t800-bootstrap (аудит + глобальное правило по согласию)"
Write-Host "Далее: /t800-start для создания subagents/skills/commands/rules"
Write-Host "Перезапустите Cursor (Reload Window)."
