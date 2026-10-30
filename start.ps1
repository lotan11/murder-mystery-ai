[CmdletBinding()]
param(
    [ValidateRange(1, 65535)][int]$Port = 8000,
    [switch]$Lan,
    [switch]$SkipSetup,
    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    $pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        if ($SkipSetup) { throw 'Run without -SkipSetup once to prepare the app.' }
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python environment setup failed. Install Python 3.11+ with Python on PATH.' }
    }
    if (-not $SkipSetup) {
        & $pythonPath -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
        Push-Location frontend
        try {
            & npm.cmd ci
            if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed. Install Node.js 20.19+.' }
            & npm.cmd run build
            if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
        } finally { Pop-Location }
    }
    if (-not (Test-Path -LiteralPath 'frontend\dist\index.html')) {
        throw 'Frontend build is missing. Run again without -SkipSetup.'
    }
    $bindAddress = if ($Lan) { '0.0.0.0' } else { '127.0.0.1' }
    Write-Host "Open http://localhost:$Port and create an evening. Press Ctrl+C to stop."
    if ($Lan) { Write-Host 'For guests, open the app using this computer''s LAN IPv4 address, then share its guest link.' }
    # Binary microphone clips are separately capped at 512 KiB by the listener; the app still validates every text command.
    $serverArguments = @('-m', 'uvicorn', 'backend.main:app', '--host', $bindAddress, '--port', "$Port", '--ws-max-size', '614400', '--no-access-log', '--log-level', 'warning')
    if ($EnvFile) {
        $resolvedEnvFile = (Resolve-Path -LiteralPath $EnvFile).Path
        if (-not (Test-Path -LiteralPath $resolvedEnvFile -PathType Leaf)) { throw 'The selected environment file is missing.' }
        $serverArguments += @('--env-file', $resolvedEnvFile)
    }
    & $pythonPath @serverArguments
    if ($LASTEXITCODE -ne 0) { throw 'Server stopped with an error. Check whether the port is already in use.' }
} finally { Pop-Location }
