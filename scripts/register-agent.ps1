# Adds or updates an agent entry in registry/agents-registry.json
# Usage: .\scripts\register-agent.ps1 -Id my-agent -File agents/my-agent.md -Category content -Description "..." [-Readonly] [-Calls "a,b"] [-CalledBy "t-800-factory"]

param(
    [Parameter(Mandatory = $true)][string]$Id,
    [Parameter(Mandatory = $true)][string]$File,
    [Parameter(Mandatory = $true)][string]$Category,
    [Parameter(Mandatory = $true)][string]$Description,
    [switch]$Readonly,
    [string]$Calls = "",
    [string]$CalledBy = "t-800-factory"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$registryPath = Join-Path $root "registry\agents-registry.json"

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding utf8 | ConvertFrom-Json

$callsList = @()
if ($Calls) { $callsList = $Calls -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ } }

$calledByList = @()
if ($CalledBy) { $calledByList = $CalledBy -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ } }

$entry = [PSCustomObject]@{
    id          = $Id
    file        = $File.Replace('\', '/')
    category    = $Category
    readonly    = [bool]$Readonly
    calls       = $callsList
    calledBy    = $calledByList
    description = $Description
}

$existing = @($registry.agents | Where-Object { $_.id -eq $Id })
if ($existing.Count -gt 0) {
    $registry.agents = @($registry.agents | Where-Object { $_.id -ne $Id }) + $entry
    Write-Host "Updated registry entry: $Id" -ForegroundColor Cyan
} else {
    $registry.agents = @($registry.agents) + $entry
    Write-Host "Added registry entry: $Id" -ForegroundColor Cyan
}

$registry.updated = (Get-Date -Format "yyyy-MM-dd")
$registry | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $registryPath -Encoding utf8

Write-Host "Run .\scripts\audit-agent-graph.ps1 to verify symmetry." -ForegroundColor DarkGray
