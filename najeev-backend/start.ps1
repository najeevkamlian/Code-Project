$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed.' }
    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
if (-not (Test-Path '.env')) { throw 'Create .env from .env.example and set your secrets first.' }
$docker = Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin\docker.exe'
& $docker compose up -d
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop and wait for its engine to be ready.' }
& $python -m app.wait_for_databases
if ($LASTEXITCODE -ne 0) { throw 'Databases did not become ready.' }
& $python -m app.seed
if ($LASTEXITCODE -ne 0) { throw 'Database seed failed.' }
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
