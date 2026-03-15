# Phase 3: API and Interface - Research

**Researched:** 2026-03-15
**Domain:** Python API Design / CLI Development
**Confidence:** HIGH

## Summary

Phase 3 wraps the semantic search core (built in Phase 2) with user-facing interfaces: a Python API for programmatic access and a CLI for interactive queries. The SemanticSearch class already exists with `build_index()`, `search()`, `save_index()`, and `load_index()` methods. This phase requires exposing it properly through the package and adding a CLI tool.

**Primary recommendation:** Use **Click** for CLI (mature, well-documented, extensive ecosystem) combined with **rich** for formatted output. Create a high-level `MediaSearch` class that combines dataset loading and search in one step for simpler Python API usage.

## User Constraints

### Locked Decisions
- SemanticSearch class from Phase 2 (already implemented)
- Pydantic v2 for data models
- JSON format for dataset storage
- SearchResult and SearchResponse models already defined

### Claude's Discretion
- CLI framework selection (Click vs Typer vs argparse)
- CLI output format (JSON vs table vs simple list)
- High-level API wrapper design
- Module organization (single entry point vs multiple)

### Deferred Ideas (OUT OF SCOPE)
- Web-based search interface (UI-01 in v2)
- Image preview in results (UI-02 in v2)
- Filtering by category/tag (ADV-01 in v2)
- Authentication/multi-user support

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Click | 8.1+ | CLI framework | Industry standard; decorator-based; extensive ecosystem |
| rich | 13+ | Terminal output formatting | Pairs well with Click; tables, colors, progress |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typer | 0.9+ | Alternative CLI framework | If prefer type-hint based CLI |
| tabulate | 0.9+ | Table formatting | Alternative to rich for simpler tables |
| json | stdlib | JSON output | Built-in for API output |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Click | Typer | Typer: cleaner with type hints, Click: more mature, more plugins |
| Click | argparse | argparse: stdlib, more verbose; Click: easier subcommands |
| rich | tabulate | rich: more features, colors; tabulate: simpler, less deps |

**Installation:**
```bash
pip install click rich
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── __init__.py              # Package exports
├── api/
│   ├── __init__.py
│   └── media_search.py      # High-level MediaSearch API
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point
└── ... (existing modules)
```

### Pattern 1: High-Level Search API
**What:** One-line search from dataset file

**When to use:** Simplest Python API for users

**Example:**
```python
from src.api import MediaSearch

# Simple one-liner search
search = MediaSearch("data/dataset.json")
results = search.query("cats on windowsill", top_k=10)

# Results have: path, score, description, media_type, format
for r in results:
    print(f"{r.path} (score: {r.score})")
```

**Implementation:**
```python
class MediaSearch:
    """High-level media search API.

    Combines dataset loading, index building, and searching
    into a single simple interface.
    """

    def __init__(self, dataset_path: str, index_path: str | None = None):
        """Initialize with dataset and optional saved index."""
        self.dataset_path = dataset_path
        self.dataset = MediaDataset.load(dataset_path)
        self.search = SemanticSearch()
        if index_path and Path(index_path).exists():
            self.search = SemanticSearch.load_index(index_path)
        else:
            self.search.build_index(self.dataset)

    def query(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search for media matching query."""
        return self.search.search(query, top_k).results
```

### Pattern 2: CLI with Click
**What:** Command-line interface using Click decorators

**When to use:** Interactive search from terminal

**Example:**
```bash
# Simple search
media-search search "sunset over mountains"

# With options
media-search search "cat" --top 10 --format json

# Build index separately
media-search build-index data/dataset.json
```

**Implementation:**
```python
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def cli():
    """Media Dataset Search CLI."""
    pass

@cli.command()
@click.argument("query")
@click.option("--top", "-n", default=5, help="Number of results")
@click.option("--format", "-f", type=click.Choice(["table", "json", "simple"]), default="table")
@click.option("--dataset", default="data/dataset.json", help="Path to dataset")
def search(query: str, top: int, format: str, dataset: str):
    """Search for media items matching QUERY."""
    search_api = MediaSearch(dataset)
    results = search_api.query(query, top_k=top)

    if format == "json":
        import json
        console.print_json(data=[r.model_dump() for r in results])
    elif format == "simple":
        for r in results:
            console.print(f"{r.score:.4f}  {r.path}")
    else:  # table
        table = Table(title=f"Search: '{query}'")
        table.add_column("Score", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Description")
        for r in results:
            table.add_row(f"{r.score:.4f}", r.path, r.description[:60])
        console.print(table)
```

### Pattern 3: Python Package Exports
**What:** Clean public API through __init__.py

**When to use:** Users import from package root

**Example:**
```python
from src import MediaSearch, SemanticSearch, MediaDataset

# High-level API
search = MediaSearch("data/dataset.json")
results = search.query("query")

# Low-level API
dataset = MediaDataset.load("data/dataset.json")
search_engine = SemanticSearch()
search_engine.build_index(dataset)
results = search_engine.search("query")
```

**Implementation (src/__init__.py):**
```python
"""Multimedia Dataset Retrieval System."""

from src.api.media_search import MediaSearch
from src.models.media import MediaDataset, MediaItem
from src.search import SemanticSearch, SearchResult, SearchResponse

__all__ = [
    "MediaSearch",
    "MediaDataset",
    "MediaItem",
    "SemanticSearch",
    "SearchResult",
    "SearchResponse",
]
```

### Pattern 4: Entry Points
**What:** CLI command available after pip install

**When to use:** Users install package and run command

**Implementation (pyproject.toml):**
```toml
[project.scripts]
media-search = "src.cli.main:cli"
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | argparse or manual sys.argv | Click | Handles help, subcommands, validation automatically |
| Terminal colors | ANSI escape codes | rich | Cross-platform, consistent, easy API |
| JSON serialization | Manual dict construction | Pydantic .model_dump() | Type-safe, handles nested models |

**Key insight:** For CLI tools, user experience matters more than minimal dependencies. rich + Click is worth the extra dependency for significantly better output and easier maintenance.

## Common Pitfalls

### Pitfall 1: Forgetting to Build Index
**What goes wrong:** Users call search() but get empty results
**Why it happens:** Index not built; code assumes pre-built index
**How to avoid:** Auto-build on first search if no saved index exists; provide clear error message
**Warning signs:** Empty results array, "index not built" errors

### Pitfall 2: Relative Path Resolution
**What goes wrong:** Paths in results don't resolve correctly
**Why it happens:** Dataset at different location than media files
**How to avoid:** Store base_path with dataset; resolve paths relative to dataset location
**Warning signs:** File not found errors when using returned paths

### Pitfall 3: Missing Dependencies in CLI
**What goes wrong:** CLI fails to import due to missing packages
**Why it happens:** Click/rich not in core dependencies
**How to avoid:** Add CLI as optional dependency group
**Warning signs:** ImportError when running CLI command

### Pitfall 4: Large Index Load Time
**What goes wrong:** CLI feels slow on startup
**Why it happens:** Loading embedding model and index takes time
**How to avoid:** Lazy initialization; show progress; consider cached index
**Warning signs:** Multiple seconds before first output

## Code Examples

### CLI with Multiple Commands
```python
# src/cli/main.py
import click
from pathlib import Path

@click.group()
def cli():
    """Media Dataset Search - Find images and videos by description."""
    pass

@cli.command()
@click.argument("query")
@click.option("-n", "--top", default=5, help="Number of results")
@click.option("-d", "--dataset", default="data/dataset.json", help="Dataset path")
def search(query, top, dataset):
    """Search for media matching QUERY."""
    from src.api import MediaSearch
    search_api = MediaSearch(dataset)
    results = search_api.query(query, top_k=top)
    # ... display results

@cli.command()
@click.argument("dataset")
@click.option("-o", "--output", default="data/index.pkl", help="Index output path")
def build(dataset, output):
    """Build search index from DATASET."""
    from src.api import MediaSearch
    from src.search import SemanticSearch

    dataset = MediaDataset.load(dataset)
    search = SemanticSearch()
    search.build_index(dataset)
    search.save_index(output)
    click.echo(f"Index built with {len(search)} items")

if __name__ == "__main__":
    cli()
```

### Python API Usage
```python
# Example: Using the high-level API
from src.api import MediaSearch

# Initialize (loads dataset, builds index)
search = MediaSearch("data/dataset.json")

# Search
results = search.query("a cat sleeping on a couch", top_k=5)

# Results contain: path, score, description, media_type, format
for r in results:
    print(f"Score: {r.score:.2%}")
    print(f"Path:  {r.path}")
    print(f"Type:  {r.media_type} ({r.format})")
    print(f"Desc:  {r.description}")
    print()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| argparse | Click/Typer | ~2015+ | Declarative syntax reduces boilerplate |
| print statements | rich/clickecho | ~2018+ | Formatted output improves UX |
| Manual JSON | Pydantic .model_dump() | ~2020+ | Type-safe serialization |
| Global state | Dependency injection | ~2015+ | Testable, composable code |

**Deprecated/outdated:**
- **optparse:** Deprecated since Python 3.2; use argparse or Click
- **colorama:** Use rich instead; richer formatting
- **sys.argv parsing:** Use Click/Typer for proper CLI

## Open Questions

1. **Should the CLI support interactive mode?**
   - What we know: Click supports prompt() for user input
   - What's unclear: Whether interactive search adds value over repeated CLI calls
   - Recommendation: Start with non-interactive; add interactive if requested

2. **How to handle missing dataset file?**
   - What we know: Current code raises FileNotFoundError
   - What's unclear: Whether to create sample dataset or show setup instructions
   - Recommendation: Show clear error with setup instructions

3. **Should index be built automatically or require explicit build?**
   - What we know: Can be slow for large datasets
   - What's unclear: User preference for explicit vs automatic
   - Recommendation: Auto-build with progress indicator; allow save for reuse

## Validation Architecture

> Section added for Nyquist compliance (config: verification.nyquist_verify = true)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Python standard) |
| Config file | pytest.ini (in pyproject.toml) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| API-01 | Python API for programmatic access | Unit | `pytest tests/test_api.py -k test_media_search_api -x` | Wave 0 |
| API-02 | CLI for interactive queries | Integration | `pytest tests/test_cli.py -k test_cli_search -x` | Wave 0 |
| API-03 | Query returns paths, scores, metadata | Unit | `pytest tests/test_api.py -k test_search_result_fields -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** Run affected test files only (`pytest tests/test_<module>.py -x -q`)
- **Per wave merge:** Run full test suite (`pytest tests/ -v`)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_api.py` — covers API-01, API-03 (Python API)
- [ ] `tests/test_cli.py` — covers API-02 (CLI)
- [ ] `src/api/__init__.py` — API module
- [ ] `src/api/media_search.py` — MediaSearch class
- [ ] `src/cli/__init__.py` — CLI module
- [ ] `src/cli/main.py` — CLI entry point
- [ ] `src/__init__.py` — Package exports
- [ ] Add dependencies: `pip install click rich` — if not in dependencies
- [ ] Add entry point to pyproject.toml

*(All test and implementation files are Wave 0 gaps - no API/CLI code exists yet)*

## Sources

### Primary (HIGH confidence)
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework
- [Rich Documentation](https://rich.readthedocs.io/) - Terminal formatting
- [Pydantic Documentation](https://docs.pydantic.dev/) - Model serialization

### Secondary (MEDIUM confidence)
- [Typer Documentation](https://typer.tiangolo.com/) - Alternative CLI framework (for comparison)
- [Python Packaging Guide](https://packaging.python.org/) - Entry points

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Click/rich are well-established industry standards
- Architecture: HIGH - patterns follow Python ecosystem best practices
- Pitfalls: HIGH - documented from real-world CLI/API experience

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (30 days - CLI/API patterns stable)

---

*Phase: 03-api-and-interface*
*Research gathered: 2026-03-15*
