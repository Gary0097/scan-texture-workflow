[CmdletBinding(DefaultParameterSetName = 'File')]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'File')]
    [string]$ScriptPath,

    [Parameter(Mandatory = $true, ParameterSetName = 'Code')]
    [string]$Code,

    [string]$ProgId = 'Photoshop.Application',
    [switch]$LaunchIfNeeded,
    [switch]$Visible
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw 'Run this helper with Windows PowerShell 5.1 (powershell.exe), not PowerShell 7 (pwsh).'
}

if ($PSCmdlet.ParameterSetName -eq 'File') {
    $resolvedScript = (Resolve-Path -LiteralPath $ScriptPath).Path
    if ([System.IO.Path]::GetExtension($resolvedScript) -notin @('.jsx', '.js')) {
        throw 'Photoshop scripts must use a .jsx or .js extension.'
    }
    $Code = [System.IO.File]::ReadAllText($resolvedScript, [System.Text.Encoding]::UTF8)
}

if ([string]::IsNullOrWhiteSpace($Code)) {
    throw 'The Photoshop script is empty.'
}

try {
    $photoshop = [Runtime.InteropServices.Marshal]::GetActiveObject($ProgId)
} catch {
    if (-not $LaunchIfNeeded) {
        throw "No running Photoshop COM instance is available for '$ProgId'. Start Photoshop and wait until it is ready, or pass -LaunchIfNeeded explicitly."
    }
    $photoshop = New-Object -ComObject $ProgId
}

if ($Visible) {
    $photoshop.Visible = $true
}

try {
    $result = $photoshop.DoJavaScript($Code)
    if ($null -ne $result) {
        $result
    }
} finally {
    if ($null -ne $photoshop -and [Runtime.InteropServices.Marshal]::IsComObject($photoshop)) {
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($photoshop)
    }
}
