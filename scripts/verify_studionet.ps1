$ErrorActionPreference = 'Stop'

$expectedRpc = 'https://studio.genlayer.com/api'
$expectedChain = '61999'

if (-not (Get-Command genlayer -ErrorAction SilentlyContinue)) {
    throw 'genlayer CLI not found'
}

$info = genlayer network info 2>&1 | Out-String
Write-Output $info

if ($info -notmatch "alias:\s*'studionet'") {
    throw 'Refusing to continue: the effective network alias is not studionet'
}

if ($info -notmatch [regex]::Escape($expectedChain)) {
    throw "Refusing to continue: expected chain ID $expectedChain"
}
if ($info -notmatch [regex]::Escape($expectedRpc)) {
    throw "Refusing to continue: expected RPC $expectedRpc"
}

Write-Output 'Studionet network guard: PASS'
