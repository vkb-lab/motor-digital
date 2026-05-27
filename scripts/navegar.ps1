param(
    [Parameter(Mandatory=$true)]
    [string]$Query
)

Set-Location "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\activate") {
    . .\venv\Scripts\activate
}

python -m k_atlas.services.browser_operator "$Query"