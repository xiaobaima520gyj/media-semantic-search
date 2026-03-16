English | [中文](./README.md)

# Media Dataset Retrieval System - User Guide

## Overview

This is a semantic search system for retrieving images and videos using natural language descriptions. The system uses AI embedding models to convert text into vectors and finds the most relevant media files through semantic similarity matching.

### Language Support

- **Default Model**: English-optimized (all-MiniLM-L6-v2)
- **Multilingual Model**: Supports Chinese, English, and 50+ languages (paraphrase-multilingual-MiniLM-L12-v2)

## Quick Start

### 1. Installation

```bash
# Clone the project and install dependencies (includes CLI)
pip install -e ".[cli]"

# Install server dependencies (for API server mode)
pip install -e ".[server]"

# Or install all dependencies
pip install -e ".[cli,server]"

# Or install core dependencies only
pip install -e .
```

### 2. Prepare Dataset

Create a `data/dataset.json` file with the following format:

```json
{
  "version": "1.0",
  "items": [
    {
      "id": "img_001",
      "path": "sample/images/cat.jpg",
      "description": "A sleeping orange tabby cat curled up on a sunny windowsill",
      "media_type": "image",
      "format": "jpg",
      "categories": ["animals", "pets", "cats"],
      "tags": ["sleeping", "orange", "windowsill"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Field Description:**

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier |
| `path` | Yes | Relative file path |
| `description` | Yes | Media description (semantic search is based on this field) |
| `media_type` | Yes | `image` or `video` |
| `format` | Yes | File format (e.g., jpg, png, mp4) |
| `categories` | No | List of category tags |
| `tags` | No | List of keyword tags |

### 3. Execute Search

```bash
# Basic search (returns top 5 results)
media-search search "cats on windowsill"

# Specify number of results
media-search search "sunset" --top 10

# JSON format output
media-search search "sunset" --format json

# Simple format output
media-search search "beach" --format simple
```

### 4. Quick Start (Recommended)

The project provides convenient scripts for quick startup:

| Script | Purpose |
|--------|---------|
| `run_server.bat` | Start API server (model stays in memory) |
| `run_test.bat` | Start chat-style test client |

**Usage Flow:**

1. Double-click `run_server.bat` to start the API server (keep it running)
2. Double-click `run_test.bat` to open the chat-style search interface
3. Enter your query to search

★ Insight ─────────────────────────────────────
- Server mode loads the model once; subsequent searches are very fast
- Chat client supports Chinese input with better interactivity
- Suitable for frequent search scenarios
─────────────────────────────────────────────────

## Command Reference

### search - Semantic Search

```bash
media-search search <QUERY> [OPTIONS]
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--top` | `-n` | 5 | Number of results to return |
| `--format` | `-f` | table | Output format: table/json/simple |
| `--dataset` | `-d` | data/dataset.json | Dataset file path |
| `--index` | `-i` | None | Pre-built index path (faster loading) |

**Examples:**
```bash
# Table output (default)
media-search search "technology innovation"

# JSON output (for program processing)
media-search search "nature landscape" --format json --top 20

# Use pre-built index for faster startup
media-search search "cat" --index data/index.pkl
```

### build-index - Build Index

Pre-building an index can significantly speed up search startup:

```bash
media-search build-index <DATASET> [OPTIONS]
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | data/index.pkl | Index output path |
| `--model` | `-m` | all-MiniLM-L6-v2 | Embedding model name |

**Examples:**
```bash
# Build index
media-search build-index data/dataset.json -o data/index.pkl

# Subsequent searches use the index
media-search search "sunset" --index data/index.pkl
```

### server - API Server

Start a FastAPI server with the model loaded in memory for faster subsequent searches:

```bash
media-search server [OPTIONS]
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--dataset` | `-d` | data/dataset.json | Dataset file path |
| `--index` | `-i` | None | Pre-built index path |
| `--model` | `-m` | all-MiniLM-L6-v2 | Embedding model name |
| `--port` | `-p` | 8000 | Server port |
| `--host` | | 127.0.0.1 | Server address |

**Examples:**
```bash
# Start server (Chinese mode)
media-search server -d data/dataset.json -i data/index_zh.pkl -m paraphrase-multilingual-MiniLM-L12-v2 -p 8000
```

★ Insight ─────────────────────────────────────
- After server starts, the model is loaded once; subsequent searches take only tens of milliseconds
- Suitable for high-frequency search scenarios
- Can be integrated into other applications via HTTP API
─────────────────────────────────────────────────

## API Server

After starting the server, the following HTTP endpoints are available:

### Endpoint List

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic search |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation (Swagger UI) |

### Usage Examples

**curl:**
```bash
# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to find a cat", "top_k": 5}'

# Health check
curl http://localhost:8000/health
```

**Python:**
```python
import requests

# Search
response = requests.post(
    "http://localhost:8000/search",
    json={"query": "I want to find a cat", "top_k": 5}
)
results = response.json()

# View results
for r in results["results"]:
    print(f"{r['score']:.4f} - {r['path']}")
```

### Interactive Documentation

Visit `http://localhost:8000/docs` to view and test all API endpoints.

★ Insight ─────────────────────────────────────
- Swagger UI provides online testing capabilities
- No need to write code to debug the API
- Supports client code generation
─────────────────────────────────────────────────

## Python API Usage

### Basic Usage

```python
from src.api import MediaSearch

# Initialize search (loads dataset)
search = MediaSearch("data/dataset.json")

# Execute search
results = search.query("cats", top_k=5)

# Iterate through results
for result in results:
    print(f"Path: {result.path}")
    print(f"Similarity: {result.score:.4f}")
    print(f"Description: {result.description}")
    print(f"Type: {result.media_type}/{result.format}")
    print("---")
```

### Using Pre-built Index

```python
from src.api import MediaSearch

# Initialize with pre-built index (faster)
search = MediaSearch("data/dataset.json", index_path="data/index.pkl")

# Execute search
results = search.query("sunset beach", top_k=10)
```

### Building Index Manually

```python
from src.models.media import MediaDataset
from src.search import SemanticSearch

# Load dataset
media_dataset = MediaDataset.load("data/dataset.json")

# Build index
search = SemanticSearch()
search.build_index(media_dataset)

# Save index
search.save_index("data/index.pkl")
```

## Chinese Search

The system supports Chinese semantic search. Use the multilingual model:

### CLI Method

```bash
# Build index with multilingual model
media-search build-index data/dataset.json -o data/index_zh.pkl --model paraphrase-multilingual-MiniLM-L12-v2

# Chinese search
media-search search "熊猫" --index data/index_zh.pkl
```

### Python API Method

```python
from src.models.media import MediaDataset
from src.search import SemanticSearch, MULTILINGUAL_MODEL

# Load dataset
media_dataset = MediaDataset.load("data/dataset.json")

# Use multilingual model
search = SemanticSearch(model_name=MULTILINGUAL_MODEL)
search.build_index(media_dataset)

# Chinese search
results = search.search("熊猫")

# Mixed Chinese-English search
results = search.search("可爱的猫咪和狗狗")
```

### Multilingual Hybrid Search

Supports mixed Chinese-English queries:

```python
results = search.search("可爱的小猫 cute cat")
```

★ Insight ─────────────────────────────────────
- Multilingual model has the same vector dimension (384) as the default model, can be replaced directly
- Rebuild the index after switching models
- Recommend creating separate indexes for different languages
─────────────────────────────────────────────────

## Output Format Examples

### Table Format (Default)

```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┬─────────┬────────────────────────────────────────┓
┃  Score  ┃       Path         ┃  Type   ┃            Description                 ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0.8542  │ sample/images/cat… │ image/… │ A sleeping orange tabby cat curled…    │
│ 0.7231  │ sample/videos/…   │ video/… │ A cat video in a sunny room           │
└─────────┴────────────────────┴─────────┴────────────────────────────────────────┘
```

### JSON Format

```json
[
  {
    "id": "img_001",
    "path": "sample/images/cat.jpg",
    "description": "A sleeping orange tabby cat...",
    "media_type": "image",
    "format": "jpg",
    "categories": ["animals", "pets"],
    "tags": ["sleeping", "orange"],
    "score": 0.8542
  }
]
```

### Simple Format

```
0.8542  sample/images/cat.jpg
0.7231  sample/videos/cat_video.mp4
```

## FAQ

### Q: Search results are not accurate?

A: Check the `description` field in your dataset. Semantic search relies on the quality of description text.

### Q: First search is slow?

A: Use the `build-index` command to pre-build an index; subsequent searches will be much faster.

### Q: What file formats are supported?

A: The system doesn't process files directly, only stores paths. Supported formats depend on your actual media files; just record `media_type` and `format` in the database.

### Q: How to add new media entries?

A: Simply edit `dataset.json` and add new item objects. No need to rebuild the index.

### Q: How to make search faster?

A: Two ways:
1. Use pre-built index: `media-search search "query" --index data/index.pkl`
2. Start API server: Double-click `run_server.bat`, model stays in memory, subsequent searches take only tens of milliseconds

### Q: Why does every CLI search reload the model?

A: Each CLI execution is a new process, and model memory is released after the process ends. Solutions:
1. Use API server mode (recommended)
2. Or ensure the model is downloaded to local cache (second run will be faster)

## Project Structure

```
rag_demo1/
├── src/
│   ├── api/              # API interfaces
│   │   └── media_search.py
│   ├── cli/              # Command-line tool
│   │   └── main.py
│   ├── models/           # Data models
│   │   └── media.py
│   ├── search/           # Search engine
│   │   ├── embedder.py
│   │   ├── index.py
│   │   └── semantic_search.py
│   ├── server/           # API server
│   │   └── main.py
│   └── validators/       # Data validation
│       └── dataset_validator.py
├── data/
│   ├── dataset.json      # Sample dataset
│   ├── index.pkl        # Pre-built index
│   └── sample/           # Sample media files
│       ├── images/
│       └── videos/
├── tests/                # Test cases
├── run_server.bat       # Quick server startup (double-click to run)
└── run_test.bat         # Quick test client startup (double-click to run)
```

## Performance Notes

- **Dataset size**: Recommended < 10,000 items
- **CLI first search**: ~3-5 seconds (model loading)
- **CLI subsequent search**: < 1 second (cached model)
- **API server search**: < 0.1 second (model stays in memory)
- **Using index**: First search < 1 second
