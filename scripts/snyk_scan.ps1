param(
    [string]$SeverityThreshold = "high"
)

if (-not $env:SNYK_TOKEN) {
    Write-Error "SNYK_TOKEN is not set. Set it in your shell first, for example: `$env:SNYK_TOKEN='your-token'"
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required for this script. Install Docker Desktop, or run Snyk CLI directly."
    exit 1
}

Write-Host "Running Snyk dependency scan..."
docker run --rm \
    -e SNYK_TOKEN=$env:SNYK_TOKEN \
    -v "${PWD}:/project" \
    -w /project \
    snyk/snyk:python \
    snyk test --file=requirements.txt --package-manager=pip --severity-threshold=$SeverityThreshold
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running Snyk code scan..."
docker run --rm \
    -e SNYK_TOKEN=$env:SNYK_TOKEN \
    -v "${PWD}:/project" \
    -w /project \
    snyk/snyk:python \
    snyk code test --severity-threshold=$SeverityThreshold
exit $LASTEXITCODE
