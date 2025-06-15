#!/bin/bash
# Download the LoRA router model from HuggingFace

URL="https://huggingface.co/adaptive-classifier/llm-router/resolve/main/model.safetensors"
FILENAME="model.safetensors"

if [ ! -f "$FILENAME" ]; then
    echo "Router safetensors file not found, downloading..."
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$FILENAME" "$URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$FILENAME" "$URL"
    else
        echo "Error: Neither curl nor wget is available. Please install one of them."
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "Download completed successfully"
    else
        echo "Download failed"
        exit 1
    fi
else
    echo "File already exists, skipping download"
fi