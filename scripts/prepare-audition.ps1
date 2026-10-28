[CmdletBinding()]
param([string]$OutputDirectory = '', [switch]$RendererOnly)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw 'Use Windows PowerShell 5: powershell -ExecutionPolicy Bypass -File .\scripts\prepare-audition.ps1'
}
Add-Type -AssemblyName System.Speech
Add-Type -ReferencedAssemblies System.Speech -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Speech.AudioFormat;
using System.Speech.Synthesis;
using System.Threading;

public class AuditionWord {
    public string Text;
    public double Start;
    public int CharacterPosition;
    public int CharacterCount;
}
public class AuditionResult {
    public string[] Words;
    public double[] Wtimes;
    public double[] Wdurations;
    public double Duration;
}
public static class WobblebottomAuditionRenderer {
    private static double WaveDuration(string path) {
        using (BinaryReader reader = new BinaryReader(File.OpenRead(path))) {
            if (new string(reader.ReadChars(4)) != "RIFF") throw new InvalidDataException("No RIFF header.");
            reader.ReadUInt32();
            if (new string(reader.ReadChars(4)) != "WAVE") throw new InvalidDataException("No WAVE header.");
            uint byteRate = 0, dataBytes = 0;
            while (reader.BaseStream.Position + 8 <= reader.BaseStream.Length) {
                string id = new string(reader.ReadChars(4));
                uint count = reader.ReadUInt32();
                long next = reader.BaseStream.Position + count + (count % 2);
                if (id == "fmt ") {
                    reader.ReadUInt16(); reader.ReadUInt16(); reader.ReadUInt32();
                    byteRate = reader.ReadUInt32();
                } else if (id == "data") dataBytes = count;
                reader.BaseStream.Position = next;
            }
            if (byteRate == 0 || dataBytes == 0) throw new InvalidDataException("No audio samples.");
            return dataBytes * 1000.0 / byteRate;
        }
    }
    public static AuditionResult Render(string voiceName, string first, string second, string path) {
        List<AuditionWord> words = new List<AuditionWord>();
        object gate = new object();
        Exception speechError = null;
        using (SpeechSynthesizer synth = new SpeechSynthesizer())
        using (ManualResetEvent completed = new ManualResetEvent(false)) {
            synth.SelectVoice(voiceName);
            synth.Rate = 0;
            synth.Volume = 100;
            synth.SpeakProgress += delegate(object sender, SpeakProgressEventArgs e) {
                if (!String.IsNullOrWhiteSpace(e.Text)) {
                    lock (gate) words.Add(new AuditionWord {
                        Text = e.Text, Start = e.AudioPosition.TotalMilliseconds,
                        CharacterPosition = e.CharacterPosition, CharacterCount = e.CharacterCount
                    });
                }
            };
            synth.SpeakCompleted += delegate(object sender, SpeakCompletedEventArgs e) {
                speechError = e.Error;
                completed.Set();
            };
            synth.SetOutputToWaveFile(path, new SpeechAudioFormatInfo(16000, AudioBitsPerSample.Sixteen, AudioChannel.Mono));
            PromptBuilder prompt = new PromptBuilder(new CultureInfo("en-US"));
            prompt.AppendText(first);
            if (!String.IsNullOrEmpty(second)) {
                prompt.AppendBreak(TimeSpan.FromMilliseconds(800));
                prompt.AppendText(second);
            }
            synth.SpeakAsync(prompt);
            if (!completed.WaitOne(TimeSpan.FromSeconds(30))) {
                synth.SpeakAsyncCancelAll();
                throw new TimeoutException("Local speech synthesis did not finish.");
            }
            if (speechError != null) throw new InvalidOperationException("Local speech synthesis failed.", speechError);
            synth.SetOutputToNull();
        }
        double duration = WaveDuration(path);
        if (words.Count == 0) throw new InvalidOperationException("The voice returned no word timing events.");
        AuditionResult result = new AuditionResult {
            Words = new string[words.Count], Wtimes = new double[words.Count],
            Wdurations = new double[words.Count], Duration = Math.Round(duration, 2)
        };
        for (int i = 0; i < words.Count; i++) {
            double start = Math.Max(0, words[i].Start);
            double next = i + 1 < words.Count ? words[i + 1].Start : duration;
            // Starts come from SAPI. Ends are estimates; cap long gaps so pauses close the mouth.
            double gap = Math.Max(1, next - start);
            double estimate = Math.Min(400, Math.Max(1, gap - Math.Min(40, gap * 0.10)));
            result.Words[i] = words[i].Text;
            result.Wtimes[i] = Math.Round(start, 2);
            result.Wdurations[i] = Math.Round(Math.Min(estimate, Math.Max(1, duration - start)), 2);
        }
        return result;
    }
}
'@

if ($RendererOnly) { return }

$repository = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repository 'data\audition'
}
$target = [IO.Path]::GetFullPath($OutputDirectory)
[IO.Directory]::CreateDirectory($target) | Out-Null
$stage = Join-Path $target ('.staging-' + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($stage) | Out-Null

$probe = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $installed = @($probe.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo })
} finally { $probe.Dispose() }
$voiceDefinitions = @(
    @{ Id = 'david'; Match = 'Microsoft David*'; Gender = 'Male' },
    @{ Id = 'zira'; Match = 'Microsoft Zira*'; Gender = 'Female' }
)
$samples = @(
    @{ Id = 'greeting'; Title = 'A formal introduction'; First = 'Good evening. I am Detective Reginald P. Wobblebottom. We will examine the evidence carefully and establish the facts.'; Second = '' },
    @{ Id = 'observation'; Title = 'An evidence review'; First = 'We should examine that observation carefully and distinguish established evidence from suspicion.'; Second = '' },
    @{ Id = 'pause'; Title = 'A considered pause'; First = 'Something is amiss.'; Second = 'A careful question helps us distinguish fact from assumption.' }
)
$voices = @()
foreach ($definition in $voiceDefinitions) {
    $voice = @($installed | Where-Object { $_.Name -like $definition.Match -and $_.Culture.Name -eq 'en-US' } | Select-Object -First 1)
    if ($voice.Count -ne 1) {
        throw "The installed English Windows voice $($definition.Id) was not found. Enable Microsoft David and Zira in Windows speech settings, then rerun. No paid service was called."
    }
    $info = $voice[0]
    $rendered = @()
    foreach ($sample in $samples) {
        $filename = "$($definition.Id)-$($sample.Id).wav"
        $path = Join-Path $stage $filename
        $timing = [WobblebottomAuditionRenderer]::Render($info.Name, $sample.First, $sample.Second, $path)
        $text = if ($sample.Second) { $sample.First + ' ' + $sample.Second } else { $sample.First }
        $rendered += [ordered]@{
            id = $sample.Id; title = $sample.Title; text = $text
            words = @($timing.Words); wtimes = @($timing.Wtimes); wdurations = @($timing.Wdurations)
            duration_ms = $timing.Duration
        }
        Write-Host "Prepared $filename ($($timing.Words.Length) timed words)."
    }
    $voices += [ordered]@{ id = $definition.Id; name = $info.Name; locale = $info.Culture.Name; gender = $definition.Gender; samples = $rendered }
}
$manifest = [ordered]@{
    version = 1; voices = $voices
    timing_source = 'SAPI SpeakProgress word starts; word durations estimated'
    speech_source = 'Installed Windows System.Speech voices; generated locally without a provider API'
}
$manifestPath = Join-Path $stage 'manifest.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
# Publish the manifest last. Only six generated, fixed-name audio files are replaced.
foreach ($definition in $voiceDefinitions) {
    foreach ($sample in $samples) {
        $filename = "$($definition.Id)-$($sample.Id).wav"
        Move-Item -LiteralPath (Join-Path $stage $filename) -Destination (Join-Path $target $filename) -Force
    }
}
Move-Item -LiteralPath $manifestPath -Destination (Join-Path $target 'manifest.json') -Force
Remove-Item -LiteralPath $stage
Write-Host 'Local audition prepared. Refresh the voice audition page.'
Write-Host 'Word starts are reported by SAPI; word durations and mouth motion are estimates, not measured visemes.'
Write-Host 'Generated files stay under ignored data/audition by default; no redistribution license is claimed.'
