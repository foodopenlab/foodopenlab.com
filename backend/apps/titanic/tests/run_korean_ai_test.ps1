# Kiwi + Ollama 통합 테스트만 실행 (단위 테스트 제외)
# 사용: apps\titanic\tests\run_korean_ai_test.ps1
# 요구: pip install -r requirements.txt, 로컬 Ollama + anpigon/eeve-korean-10.8b:latest
$ErrorActionPreference = "Stop"

$AuditorRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$Target = Join-Path $PSScriptRoot "integration\test_korean_ai_ollama.py"

Set-Location $AuditorRoot

python -m pytest $Target -v -m "integration and ollama" -o addopts=
