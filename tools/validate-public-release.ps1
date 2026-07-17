$ErrorActionPreference = 'Stop'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $python) {
    throw 'Python 3 was not found. Install Python 3 or add it to PATH.'
}

function Invoke-PythonValidator {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ScriptPath,
        [string[]]$ScriptArguments = @()
    )

    if ($python.Name -eq 'py.exe' -or $python.Name -eq 'py') {
        & $python.Source -3 $ScriptPath @ScriptArguments
    } else {
        & $python.Source $ScriptPath @ScriptArguments
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-PythonValidator -ScriptPath "$PSScriptRoot\validate-public-release.py" -ScriptArguments $args
Invoke-PythonValidator -ScriptPath "$PSScriptRoot\validate-trial-first-pages.py"
Invoke-PythonValidator -ScriptPath "$PSScriptRoot\validate-public-audience.py"
