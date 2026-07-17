$ErrorActionPreference = 'Stop'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $python) {
    throw 'Python 3 was not found. Install Python 3 or add it to PATH.'
}

if ($python.Name -eq 'py.exe' -or $python.Name -eq 'py') {
    & $python.Source -3 "$PSScriptRoot\validate-public-release.py" @args
} else {
    & $python.Source "$PSScriptRoot\validate-public-release.py" @args
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
