param([Parameter(Mandatory=$true)][ValidateSet('ps-composite-review.jsx','make-gray-lines.jsx')][string]$Name)
$ErrorActionPreference='Stop'
$projectRoot=$PSScriptRoot.Replace('\','/')
New-Item -ItemType Directory -Force -Path "$PSScriptRoot/output/composite-review" | Out-Null
$jsxText=[IO.File]::ReadAllText("$PSScriptRoot/scripts/$Name",[Text.Encoding]::UTF8).Replace('__PROJECT_ROOT__',$projectRoot)
& "$PSScriptRoot/scripts/invoke-photoshop-jsx.ps1" -Code $jsxText
