param (
    [Parameter(Mandatory=$true)]
    [string]$Url
)

try {
    $content = (Invoke-WebRequest -Uri $Url -UseBasicParsing).Content
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $hash = [BitConverter]::ToString((New-Object System.Security.Cryptography.SHA256CryptoServiceProvider).ComputeHash($bytes)) -replace '-',''
    Write-Output "$hash : $Url"
}
catch {
    Write-Error "Fehler beim Abrufen oder Verarbeiten der URL: $Url"
}
