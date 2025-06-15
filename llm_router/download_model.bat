@echo off
REM Download the LoRA router model from HuggingFace

set URL=https://huggingface.co/adaptive-classifier/llm-router/resolve/main/model.safetensors
set FILENAME=model.safetensors

if not exist "%FILENAME%" (
    echo Router safetensors file not found, downloading...
    
    REM Try with curl first (Windows 10+ has curl)
    where curl >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        curl -L -o "%FILENAME%" "%URL%"
    ) else (
        REM Try with PowerShell
        powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%FILENAME%'"
    )
    
    if %ERRORLEVEL% EQU 0 (
        echo Download completed successfully
    ) else (
        echo Download failed
        exit /b 1
    )
) else (
    echo File already exists, skipping download
)