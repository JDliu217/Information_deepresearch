[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Query,

    [string]$SessionId,

    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$null = Get-Command curl.exe -ErrorAction Stop

$requestBody = [ordered]@{ query = $Query }
if (-not [string]::IsNullOrWhiteSpace($SessionId)) {
    $requestBody.session_id = $SessionId
}
$json = ConvertTo-Json -InputObject $requestBody -Depth 5 -Compress
$temporaryBody = Join-Path ([System.IO.Path]::GetTempPath()) (
    "research-sse-" + [guid]::NewGuid().ToString("N") + ".json"
)
$utf8WithoutBom = [System.Text.UTF8Encoding]::new($false)
$url = $BaseUrl.TrimEnd([char]"/") + "/api/research/stream"

try {
    [System.IO.File]::WriteAllText($temporaryBody, $json, $utf8WithoutBom)
    & curl.exe --silent --show-error --no-buffer --request POST $url `
        --header "Content-Type: application/json; charset=utf-8" `
        --data-binary "@$temporaryBody"

    if ($LASTEXITCODE -ne 0) {
        throw "curl.exe 请求失败，退出码：$LASTEXITCODE"
    }
}
finally {
    if (Test-Path -LiteralPath $temporaryBody) {
        Remove-Item -LiteralPath $temporaryBody -Force
    }
}
