param(
  [Parameter(Mandatory=$true)]
  [string]$ApiBaseUrl,

  [string]$OutputPath = ""
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

$artifactResults = @()
foreach ($artifact in $result.artifacts) {
  if ($artifact.artifact_type -in @("musicxml", "midi")) {
    $artifactUri = $artifact.uri
    $artifactUrl = if ($artifactUri.StartsWith("http")) { $artifactUri } else { "$ApiBaseUrl$artifactUri" }
    $artifactResponse = Invoke-WebRequest $artifactUrl
    if ($artifactResponse.StatusCode -ne 200 -or $artifactResponse.RawContentLength -le 0) {
      throw "Artifact download failed for $($artifact.artifact_type)"
    }
    $artifactResults += [ordered]@{
      artifact_type = $artifact.artifact_type
      uri = $artifactUri
      status_code = $artifactResponse.StatusCode
      byte_count = $artifactResponse.RawContentLength
      content_type = $artifactResponse.Headers["Content-Type"]
    }
  }
}

$evidence = [ordered]@{
  api_base_url = $ApiBaseUrl
  health = $health
  version = $version
  sample_transcription = [ordered]@{
    sample_id = $samples[0].sample_id
    job_id = $result.job_id
    status = $result.status
    detector_mode = $result.detector_mode
    assembly_mode = $result.assembly_mode
    detection_count = $result.detection_count
    relationship_count = $result.relationship_count
    warnings = $result.warnings
  }
  artifact_downloads = $artifactResults
  passed = $true
}

if ($OutputPath) {
  $parent = Split-Path -Parent $OutputPath
  if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
  }
  $evidence | ConvertTo-Json -Depth 20 | Set-Content -Encoding utf8 $OutputPath
}

Write-Host "Melodious V2 AWS smoke test passed for $ApiBaseUrl"
if ($OutputPath) {
  Write-Host "Evidence written to $OutputPath"
}
