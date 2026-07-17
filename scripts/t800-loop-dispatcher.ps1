# t800-loop-dispatcher.ps1 — observe-only loop notice (fail-open), parity with .sh
# Usage: .\scripts\t800-loop-dispatcher.ps1 [-MemoryPath PATH] [-Workspace PATH]
# Never writes secrets. Always exit 0.

param(
    [string]$MemoryPath = $env:T800_MEMORY_PATH,
    [string]$Workspace = $(if ($env:T800_WORKSPACE) { $env:T800_WORKSPACE } elseif ($env:CURSOR_PROJECT_DIR) { $env:CURSOR_PROJECT_DIR } else { (Get-Location).Path })
)

$ErrorActionPreference = "Continue"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$PluginRoot = Split-Path -Parent $Here
$LogDir = if ($env:T800_LOOP_LOG_DIR) { $env:T800_LOOP_LOG_DIR } else { Join-Path $PluginRoot ".t-800-logs" }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir "loop-dispatcher.log"

function Write-Log([string]$Msg) {
    try {
        $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Msg
        Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
    } catch {}
}

if (-not $MemoryPath) {
    $discover = Join-Path $Here "discover-target-project.sh"
    if (Test-Path $discover) {
        try {
            $raw = & bash $discover --workspace $Workspace --plugin-root $PluginRoot 2>$null
            $jsonStart = $raw.LastIndexOf("{")
            if ($jsonStart -ge 0) {
                $obj = $raw.Substring($jsonStart) | ConvertFrom-Json
                $MemoryPath = $obj.memory_path
            }
        } catch {
            Write-Log "discover failed"
        }
    }
}

if (-not $MemoryPath) {
    Write-Log "skip: no memory_path"
    exit 0
}

try {
    New-Item -ItemType Directory -Force -Path $MemoryPath | Out-Null
} catch {}

$paused = Join-Path $MemoryPath ".loop-paused"
if (Test-Path $paused) {
    Write-Log "paused: $paused"
    exit 0
}

$ready = $false
$packsDir = Join-Path $MemoryPath "fix-packs"
if (Test-Path $packsDir) {
    $packs = Get-ChildItem -Path $packsDir -Filter "loop-low-*.md" -ErrorAction SilentlyContinue
    if ($packs -and $packs.Count -gt 0) { $ready = $true }
}

if (-not $ready) {
    $runs = Join-Path $MemoryPath "runs"
    if (Test-Path $runs) {
        Get-ChildItem -Path $runs -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $lessons = Join-Path $_.FullName "lessons.json"
            if (Test-Path $lessons) {
                try {
                    $data = Get-Content -Raw -Path $lessons | ConvertFrom-Json
                    foreach ($lesson in @($data.lessons)) {
                        if ($lesson.risk_class -and ($lesson.risk_class.ToString().ToUpper() -eq "LOW")) {
                            $files = @()
                            if ($lesson.proposed_patch -and $lesson.proposed_patch.files) {
                                $files = @($lesson.proposed_patch.files)
                            }
                            if ($files.Count -gt 0) { $ready = $true; break }
                        }
                    }
                } catch {}
            }
            if ($ready) { break }
        }
    }
}

$noticeDir = Join-Path $MemoryPath "loop"
New-Item -ItemType Directory -Force -Path $noticeDir | Out-Null | Out-Null

if ($ready) {
    $notice = Join-Path $noticeDir "session-notice.txt"
    $marker = Join-Path $noticeDir "low-risk-ready.marker"
    @"
T-800 loop: есть low-risk элементы в очереди.
Запустите /t800-loop (semi-manual), затем /t800-fix по pack.
Пауза: создайте файл $paused
"@ | Set-Content -Path $notice -Encoding UTF8
    (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") | Set-Content -Path $marker -Encoding UTF8
    Write-Log "notice written: $notice"
} else {
    $marker = Join-Path $noticeDir "low-risk-ready.marker"
    if (Test-Path $marker) { Remove-Item $marker -Force -ErrorAction SilentlyContinue }
    Write-Log "no low-risk packs"
}

exit 0
