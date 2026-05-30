param(
  [Parameter(Mandatory=$true)]
  [string]$ApiBaseUrl
)

$health = Invoke-RestMethod "$ApiBaseUrl/health"
if ($health.status -ne "ok") {
  throw "Health check failed"
}

$version = Invoke-RestMethod "$ApiBaseUrl/version"
if (-not $version.schema_version) {
  throw "Version check failed"
}

$samples = Invoke-RestMethod "$ApiBaseUrl/samples"
if ($samples.Count -lt 1) {
  throw "No samples returned"
}

$body = @{ sample_id = $samples[0].sample_id; requested_assembly_mode = "auto" } | ConvertTo-Json
$result = Invoke-RestMethod "$ApiBaseUrl/transcriptions" -Method Post -ContentType "application/json" -Body $body
if ($result.status -ne "complete") {
  throw "Sample transcription failed"
}

Write-Host "Melodious V2 AWS smoke test passed for $ApiBaseUrl"

