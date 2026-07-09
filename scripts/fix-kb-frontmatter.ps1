# Repairs broken YAML frontmatter in KB cards (--- followed by ## title:)
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$kb = Join-Path $root "knowledge-base"
$fixed = 0

Get-ChildItem -Path $kb -Recurse -Filter "*.md" | Where-Object {
    $_.FullName -notmatch '\\(raw|drafts)\\'
} | ForEach-Object {
    $content = Get-Content -LiteralPath $_.FullName -Raw -Encoding utf8
    if ($content -match '(?s)^---\r?\n\r?\n## title:') {
        $content = $content -replace '(?s)^---\r?\n\r?\n## title:\s*"([^"]+)"\r?\n', "---`r`ntitle: `"`$1`"`r`n"
        $content = $content -replace 'source:\s*\[([^\]]+)\]\([^\)]+\)', 'source: $1'
        if ($content -notmatch '(?s)---\r?\n[^\r\n]+\r?\n---') {
            $content = $content -replace '(?s)(last_synced:\s*\d{4}-\d{2}-\d{2})\r?\n\r?\n(## )', "`$1`r`n---`r`n`r`n`$2"
        }
        $out = $content.TrimEnd() + "`r`n"
        Set-Content -LiteralPath $_.FullName -Value $out -Encoding utf8
        $fixed++
        Write-Host "Fixed: $($_.Name)"
    }
}

Write-Host "Done. Fixed $fixed file(s)." -ForegroundColor Green
