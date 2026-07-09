# Sync Cursor docs → raw/ + drafts/ + manifest + UPDATE-QUEUE
# Usage: .\scripts\sync-docs.ps1 [-MaxPages 80] [-StaleDays 30]

param(
    [int]$MaxPages = 80,
    [int]$DelayMs = 500,
    [int]$StaleDays = 30
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$rawDir = Join-Path $root "knowledge-base\raw"
$draftDir = Join-Path $root "knowledge-base\drafts"
$reportPath = Join-Path $root "knowledge-base\SYNC-REPORT.md"
$queuePath = Join-Path $root "knowledge-base\UPDATE-QUEUE.md"
$manifestPath = Join-Path $root "knowledge-base\manifest.json"

$seedUrls = @(
    "https://cursor.com/ru/docs",
    "https://cursor.com/ru/docs/get-started/quickstart",
    "https://cursor.com/ru/docs/agent/overview",
    "https://cursor.com/docs/agent/agents-window",
    "https://cursor.com/docs/agent/agent-review",
    "https://cursor.com/docs/agent/plan-mode",
    "https://cursor.com/help/ai-features/ask-mode",
    "https://cursor.com/docs/agent/debug-mode",
    "https://cursor.com/docs/agent/design-mode",
    "https://cursor.com/docs/agent/prompting",
    "https://cursor.com/docs/agent/tools/terminal",
    "https://cursor.com/docs/agent/tools/browser",
    "https://cursor.com/docs/agent/tools/search",
    "https://cursor.com/docs/agent/tools/canvas",
    "https://cursor.com/ru/docs/rules",
    "https://cursor.com/docs/skills",
    "https://cursor.com/ru/docs/subagents",
    "https://cursor.com/docs/mcp",
    "https://cursor.com/docs/agent/security",
    "https://cursor.com/docs/agent/security/run-modes",
    "https://cursor.com/docs/models-and-pricing",
    "https://cursor.com/help/models-and-usage/usage-limits",
    "https://cursor.com/docs/cloud-agent",
    "https://cursor.com/docs/cloud-agent/setup",
    "https://cursor.com/docs/cloud-agent/settings",
    "https://cursor.com/docs/cloud-agent/automations",
    "https://cursor.com/docs/hooks",
    "https://cursor.com/docs/account/teams/setup",
    "https://cursor.com/docs/account/teams/dashboard",
    "https://cursor.com/docs/integrations/github",
    "https://cursor.com/docs/integrations/slack",
    "https://cursor.com/docs/integrations/linear",
    "https://cursor.com/docs/bugbot",
    "https://cursor.com/docs/security-agents",
    "https://cursor.com/docs/cli/overview",
    "https://cursor.com/docs/cli/headless",
    "https://cursor.com/docs/sdk/typescript",
    "https://cursor.com/docs/sdk/python",
    "https://cursor.com/docs/cloud-agent/api/endpoints",
    "https://cursor.com/ru/docs/api",
    "https://cursor.com/ru/learn",
    "https://cursor.com/ru/help",
    "https://cursor.com/ru/help/ai-features/agent",
    "https://cursor.com/ru/help/ai-features/tab"
)

New-Item -ItemType Directory -Force -Path $rawDir | Out-Null
New-Item -ItemType Directory -Force -Path $draftDir | Out-Null

$manifest = @{
    last_full_sync = (Get-Date -Format "yyyy-MM-dd")
    schema_version = 1
    sources        = @(
        "https://cursor.com/ru/docs",
        "https://cursor.com/ru/learn",
        "https://cursor.com/ru/help",
        "https://cursor.com/ru/docs/api",
        "https://cursor.com/docs"
    )
    pages          = @{}
}

if (Test-Path $manifestPath) {
    try {
        $existing = Get-Content $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
        if ($existing.pages) {
            $existing.pages.PSObject.Properties | ForEach-Object {
                $manifest.pages[$_.Name] = @{
                    sha256      = $_.Value.sha256
                    last_synced = $_.Value.last_synced
                    file        = $_.Value.file
                }
            }
        }
    }
    catch {
        Write-Host "Warning: could not parse manifest.json, starting fresh." -ForegroundColor Yellow
    }
}

function Get-SafeFileName {
    param([string]$Url)
    $u = [Uri]$Url
    $path = $u.AbsolutePath.Trim("/") -replace "/", "_"
    if ([string]::IsNullOrWhiteSpace($path)) { $path = "index" }
    return ($path + ".md")
}

function Get-ContentHash {
    param([string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return ([BitConverter]::ToString($hash) -replace "-", "").ToLower()
}

function Extract-Links {
    param([string]$Content)
    $links = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($pattern in @(
            '\]\((https://cursor\.com/[^)]+)\)',
            '\]\((/(?:ru/)?(?:docs|learn|help)[^)]*)\)'
        )) {
        foreach ($m in [regex]::Matches($Content, $pattern)) {
            $href = $m.Groups[1].Value
            if ($href.StartsWith("/")) {
                $href = "https://cursor.com" + ($href -replace '^/', '/')
            }
            if ($href -match '/ru/(docs|learn|help)' -or $href -match 'cursor\.com/docs') {
                [void]$links.Add($href.Split("#")[0])
            }
        }
    }
    return $links
}

function Fetch-Page {
    param([string]$Url)
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 45 -MaximumRedirection 10 -Headers @{
            "User-Agent"      = "T-800 Agent-Sync/0.2"
            "Accept-Language" = "ru-RU,ru;q=0.9"
        }
        return @{ Ok = $true; Content = $resp.Content; Error = $null; FinalUrl = $resp.BaseResponse.ResponseUri.AbsoluteUri }
    }
    catch {
        $enUrl = $Url -replace '/ru/', '/'
        if ($enUrl -ne $Url) {
            try {
                $resp = Invoke-WebRequest -Uri $enUrl -UseBasicParsing -TimeoutSec 45 -MaximumRedirection 10
                return @{ Ok = $true; Content = $resp.Content; Error = "fallback_en"; FinalUrl = $enUrl }
            }
            catch {
                return @{ Ok = $false; Content = $null; Error = $_.Exception.Message }
            }
        }
        return @{ Ok = $false; Content = $null; Error = $_.Exception.Message }
    }
}

function New-DraftCard {
    param([string]$Url, [string]$RawContent, [string]$Status)
    $title = "Draft"
    if ($RawContent -match '<title[^>]*>([^<]+)</title>') { $title = $Matches[1].Trim() }
    $slug = Get-SafeFileName $Url
    $body = @"
---
title: "$title"
source: $Url
audience: beginner
tier: draft
status: $Status
last_synced: $(Get-Date -Format "yyyy-MM-dd")
auto_generated: true
---

> Auto draft ($Status). Requires manual rewrite for beginners.

## Simple words
(TODO)

## When to use
(TODO)

## Steps
(TODO)

## Diagram (mermaid)
(TODO)

## Common mistakes
(TODO)

## Official link
$Url
"@
    return @{ Slug = $slug; Body = $body }
}

$queue = [System.Collections.Generic.Queue[string]]::new()
$seen = @{}
foreach ($u in $seedUrls) {
    if (-not $seen.ContainsKey($u)) { $seen[$u] = $true; $queue.Enqueue($u) }
}

$ok = 0; $fail = 0; $failed = @(); $processed = 0
$updates = @()  # @{ Url, Status, File }

while ($queue.Count -gt 0 -and $processed -lt $MaxPages) {
    $url = $queue.Dequeue()
    $processed++
    Write-Host "[$processed/$MaxPages] $url"

    $result = Fetch-Page -Url $url
    if (-not $result.Ok) {
        $fail++
        $failed += @{ Url = $url; Error = $result.Error }
        continue
    }

    $fname = Get-SafeFileName $url
    $rawPath = Join-Path $rawDir $fname
    $hash = Get-ContentHash $result.Content
    $today = Get-Date -Format "yyyy-MM-dd"

    $status = "unchanged"
    if (-not $manifest.pages.ContainsKey($url)) {
        $status = "new"
    }
    elseif ($manifest.pages[$url].sha256 -ne $hash) {
        $status = "changed"
    }

    Set-Content -Path $rawPath -Value $result.Content -Encoding utf8

    if ($status -ne "unchanged") {
        $draft = New-DraftCard -Url $url -RawContent $result.Content -Status $status
        Set-Content -Path (Join-Path $draftDir $draft.Slug) -Value $draft.Body -Encoding utf8
        $updates += @{ Url = $url; Status = $status; File = "drafts/$($draft.Slug)"; Raw = "raw/$fname" }
        Write-Host "  -> $status" -ForegroundColor $(if ($status -eq "new") { "Green" } else { "Yellow" })
    }

    $manifest.pages[$url] = @{
        sha256      = $hash
        last_synced = $today
        file        = "raw/$fname"
    }

    $ok++
    foreach ($link in (Extract-Links -Content $result.Content)) {
        if (-not $seen.ContainsKey($link) -and ($queue.Count + $processed) -lt ($MaxPages + 30)) {
            $seen[$link] = $true
            $queue.Enqueue($link)
        }
    }
    Start-Sleep -Milliseconds $DelayMs
}

# Write manifest
$manifestOut = @{
    last_full_sync = (Get-Date -Format "yyyy-MM-dd")
    schema_version = 1
    sources        = $manifest.sources
    pages          = $manifest.pages
}
($manifestOut | ConvertTo-Json -Depth 5) | Set-Content -Path $manifestPath -Encoding utf8

# UPDATE-QUEUE
$queueMd = @"
# UPDATE-QUEUE

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Pending review:** $($updates.Count)

Review each item: simplify for beginners, update a card in ``knowledge-base/0X-*/``, then update ``CHANGELOG.md`` and run ``install-plugin.ps1``.

| Status | URL | Draft | Raw |
|--------|-----|-------|-----|
"@
if ($updates.Count -eq 0) {
    $queueMd += "`n| - | (net izmeneniy) | - | - |`n"
}
else {
    foreach ($u in $updates) {
        $queueMd += "`n| **$($u.Status)** | $($u.Url) | ``$($u.File)`` | ``$($u.Raw)`` |"
    }
}
$queueMd += @"


## Statuses

- **new** - page is new; create a beginner card or add it to INDEX
- **changed** - page changed; compare it with the existing beginner card
- **unchanged** - no action needed and not listed here

## After review

1. Mark the item as reviewed (remove the row or mention it in CHANGELOG)
2. ``.\scripts\install-plugin.ps1``
"@
Set-Content -Path $queuePath -Value $queueMd -Encoding utf8

# SYNC-REPORT
$report = @"
# SYNC-REPORT

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Processed:** $processed | **OK:** $ok | **Failed:** $fail
**Updates pending:** $($updates.Count) (see UPDATE-QUEUE.md)

## Failed URLs
"@
if ($failed.Count -eq 0) { $report += "`n(none)" }
else { foreach ($f in $failed) { $report += "`n- $($f.Url): $($f.Error)" } }

$report += @"


## Manifest
- Path: ``knowledge-base/manifest.json``
- Last full sync: $(Get-Date -Format "yyyy-MM-dd")
- Total pages tracked: $($manifest.pages.Count)

## Next steps
1. Review ``UPDATE-QUEUE.md``
2. Simplify drafts for beginners
3. Update ``CHANGELOG.md``
4. ``.\scripts\install-plugin.ps1``
"@
Set-Content -Path $reportPath -Value $report -Encoding utf8

Write-Host "Done. OK=$ok Failed=$fail Updates=$($updates.Count)" -ForegroundColor Green
Write-Host "  manifest: $manifestPath"
Write-Host "  queue:    $queuePath"
