@echo off
echo Starting Media Search API Server...
echo.

cd /d "%~dp0"

media-search server -d data/dataset.json -i data/index_zh.pkl -m paraphrase-multilingual-MiniLM-L12-v2 -p 8000

pause
