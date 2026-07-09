# Audits T-800 Agent KB coverage against knowledge-base/manifest.json.
# Usage: .\scripts\audit-coverage.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$kb = Join-Path $root "knowledge-base"
$manifestPath = Join-Path $kb "manifest.json"
$reportPath = Join-Path $kb "COVERAGE-REPORT.md"

if (-not (Test-Path $manifestPath)) {
    throw "Missing manifest: $manifestPath. Run scripts\sync-docs.ps1 first."
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$cards = Get-ChildItem -Path $kb -Recurse -Filter "*.md" | Where-Object {
    $_.FullName -notmatch "\\(raw|drafts)\\"
}

$sourceMap = @{}
foreach ($card in $cards) {
    $content = Get-Content -LiteralPath $card.FullName -Raw -Encoding utf8
    foreach ($m in [regex]::Matches($content, '(?m)^source:\s*(\S+)')) {
        $url = $m.Groups[1].Value.Trim()
        if (-not $sourceMap.ContainsKey($url)) { $sourceMap[$url] = @() }
        $sourceMap[$url] += $card.FullName.Substring($kb.Length + 1)
    }
}

$groupCoverage = @(
    @{
        Label = "Docs/Learn/Help overview"
        Pattern = "https://cursor.com/ru/(docs|learn|help)$"
        Card = "INDEX.md and learning paths"
    },
    @{
        Label = "Security and run modes"
        Pattern = "https://cursor.com/docs/agent/security"
        Card = "04-bezopasnost/"
    },
    @{
        Label = "Agent modes and tools"
        Pattern = "https://cursor.com/(docs|help)/agent|https://cursor.com/help/ai-features"
        Card = "02-agent-i-rezhimy/ and 09-tools/"
    },
    @{
        Label = "Rules/Skills/MCP/Subagents"
        Pattern = "https://cursor.com/(ru/)?docs/(rules|subagents)|https://cursor.com/docs/(skills|mcp)"
        Card = "03-kontekst/"
    },
    @{
        Label = "Cloud and automations"
        Pattern = "https://cursor.com/docs/cloud-agent|https://cursor.com/docs/hooks"
        Card = "10-cloud-automation/"
    },
    @{
        Label = "Team/admin/integrations"
        Pattern = "https://cursor.com/docs/account|https://cursor.com/docs/integrations|https://cursor.com/docs/bugbot|https://cursor.com/docs/security-agents|https://cursor.com/docs/models-and-pricing|https://cursor.com/help/models-and-usage"
        Card = "11-team-admin/"
    },
    @{
        Label = "Advanced developer layer"
        Pattern = "https://cursor.com/docs/(cli|sdk)|https://cursor.com/docs/cloud-agent/api"
        Card = "12-advanced-dev/"
    }
)

$rows = @()
$explicit = 0
$grouped = 0
$missing = 0

foreach ($prop in $manifest.pages.PSObject.Properties) {
    $url = $prop.Name
    $status = "missing"
    $coverage = ""

    if ($sourceMap.ContainsKey($url)) {
        $status = "explicit"
        $coverage = ($sourceMap[$url] -join ", ")
        $explicit++
    }
    else {
        foreach ($group in $groupCoverage) {
            if ($url -match $group.Pattern) {
                $status = "grouped"
                $coverage = "$($group.Label): $($group.Card)"
                $grouped++
                break
            }
        }
        if ($status -eq "missing") { $missing++ }
    }

    $rows += [ordered]@{
        status = $status
        url = $url
        coverage = $coverage
    }
}

$report = @"
# COVERAGE-REPORT

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Manifest pages:** $($rows.Count)
**Explicit cards:** $explicit
**Grouped coverage:** $grouped
**Missing:** $missing

## Summary

| Status | Count | Meaning |
|--------|-------|---------|
| explicit | $explicit | URL appears as `source:` in a beginner card |
| grouped | $grouped | URL is covered by a broader beginner/advanced card |
| missing | $missing | Needs a new card or INDEX mapping |

## Details

| Status | URL | Coverage |
|--------|-----|----------|
"@

foreach ($row in ($rows | Sort-Object status, url)) {
    $report += "`n| $($row.status) | $($row.url) | $($row.coverage) |"
}

$report += @"


## Maintainer next steps

1. Create cards for `missing` URLs.
2. If grouped coverage is too broad, split it into a dedicated card.
3. Update `INDEX.md`, `CHANGELOG.md`, then run `install-plugin.ps1`.
"@

Set-Content -LiteralPath $reportPath -Value $report -Encoding utf8
Write-Host "Coverage report: $reportPath"
Write-Host "Explicit=$explicit Grouped=$grouped Missing=$missing"

if ($missing -gt 0) {
    exit 2
}
