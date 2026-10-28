[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$InputFile,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# Load the same trusted, local C# renderer as the audition; do not generate its samples.
& (Join-Path $PSScriptRoot 'prepare-audition.ps1') -RendererOnly

$payload = [IO.File]::ReadAllText([IO.Path]::GetFullPath($InputFile), [Text.Encoding]::UTF8) | ConvertFrom-Json
if ($payload.voice -notin @('david', 'zira')) { throw 'Unsupported local voice.' }
if ($payload.text -isnot [string] -or [string]::IsNullOrWhiteSpace($payload.text) -or $payload.text.Length -gt 1500) {
    throw 'Invalid public dialogue length.'
}
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (-not [IO.Directory]::Exists($output)) { throw 'The server output directory is missing.' }

$probe = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $pattern = if ($payload.voice -eq 'david') { 'Microsoft David*' } else { 'Microsoft Zira*' }
    $installed = @($probe.GetInstalledVoices() | Where-Object {
        $_.Enabled -and $_.VoiceInfo.Name -like $pattern -and $_.VoiceInfo.Culture.Name -eq 'en-US'
    } | Select-Object -First 1)
    if ($installed.Count -ne 1) { throw 'The chosen local Windows voice is not installed.' }
    $voiceName = $installed[0].VoiceInfo.Name
} finally { $probe.Dispose() }

# Dialogue is an ordinary string in a JSON file. AppendText escapes SSML; nothing is evaluated.
$wavePath = Join-Path $output 'speech.wav'
$result = [WobblebottomAuditionRenderer]::Render($voiceName, $payload.text, '', $wavePath)
$manifest = [ordered]@{
    voice = $payload.voice; text = $payload.text
    words = @($result.Words); wtimes = @($result.Wtimes); wdurations = @($result.Wdurations)
    duration_ms = $result.Duration
}
$json = $manifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $output 'speech.json'), $json, (New-Object Text.UTF8Encoding($false)))
