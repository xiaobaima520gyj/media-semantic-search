# Phase 2: Semantic Search Core - Research

**Researched:** 2026-03-15
**Domain:** Semantic Search / Vector Embeddings
**Confidence:** HIGH

## Summary

Phase 2 implements AI-powered semantic search for the multimedia dataset. Using text descriptions, users can find relevant images/videos without filename or folder navigation. The implementation requires embedding generation (converting text to vectors), a vector index for similarity search, and a search API returning ranked results.

**Primary recommendation:** Use `sentence-transformers` with `all-MiniLM-L6-v2` model for embeddings, and `scikit-learn NearestNeighbors` with cosine similarity for the vector index. This combination meets all SRCH requirements (SRCH-01 through SRCH-04) with sub-second performance for 10K items.

## User Constraints

### Locked Decisions
- Pydantic v2 for data models (from Phase 1)
- JSON format for dataset storage
- Sample dataset at `data/dataset.json`

### Claude's Discretion
- Embedding model selection (sentence-transformers vs alternatives)
- Vector index implementation (FAISS vs sklearn vs Chroma)
- Index persistence strategy (file-based vs in-memory)
- Search result structure and scoring

### Deferred Ideas (OUT OF SCOPE)
- GPU acceleration for embeddings
- Automatic metadata extraction from media
- Hybrid search (semantic + keyword)
- Filtering by category/tag (ADV-01 in v2)

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sentence-transformers | latest (2.2+) | Text-to-embedding conversion | Industry standard; 10K+ pre-trained models; easy API |
| scikit-learn | 1.4+ | Vector similarity search | Built-in NearestNeighbors; cosine/euclidean metrics; sufficient for 10K items |
| numpy | 1.24+ | Array operations | Core dependency; handles embedding matrices |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| torch | 2.0+ | Backend for sentence-transformers | Required by sentence-transformers |
| tqdm | - | Progress bars | When building index for large datasets |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sentence-transformers | openai-embeddings | OpenAI: better quality but requires API key + cost; sentence-transformers: free, local, offline |
| sentence-transformers | huggingface-hub raw | More control but more code; sentence-transformers provides ready-to-use pipeline |
| sklearn NearestNeighbors | FAISS | FAISS: better for 1M+ vectors, GPU support; sklearn: simpler, no extra deps, exact results |
| sklearn NearestNeighbors | Chroma | Chroma: full database with filtering; sklearn: lighter, sufficient for v1 requirements |

**Installation:**
```bash
pip install sentence-transformers scikit-learn numpy torch
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── models/
│   ├── media.py           # Existing: MediaItem, MediaDataset
│   └── __init__.py
├── search/
│   ├── __init__.py
│   ├── embedder.py        # Embedding model wrapper
│   ├── index.py           # Vector index builder/searcher
│   └── search_result.py   # Search result model
└── validators/
    └── dataset_validator.py
```

### Pattern 1: Embedding-Based Search Pipeline
**What:** Convert text to embeddings, build index, query similarity

**When to use:** Any semantic search implementation

**Workflow:**
1. Load MediaDataset from JSON
2. Extract descriptions from each MediaItem
3. Generate embeddings using sentence-transformers
4. Build nearest-neighbor index
5. At query time: embed user text -> search index -> return ranked results

**Example:**
```python
# Source: https://sbert.net/ (sentence-transformers docs)
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.neighbors import NearestNeighbors

# 1. Generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
descriptions = ["A sleeping cat", "Mountain sunrise", "City night"]
embeddings = model.encode(descriptions)  # Shape: (3, 384)

# 2. Build index
index = NearestNeighbors(n_neighbors=2, metric='cosine')
index.fit(embeddings)

# 3. Query
query = "kitten on windowsill"
query_embedding = model.encode([query])
distances, indices = index.kneighbors(query_embedding)
# distances are cosine distances (lower = more similar)
# Convert to similarity: 1 - distance
```

### Pattern 2: Search Result with Scores
**What:** Return ranked results with relevance scores

**When to use:** Displaying search results to users

**Example:**
```python
from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    """Single search result with relevance score."""
    id: str
    path: str
    description: str
    media_type: str
    format: str
    score: float  # Similarity score (0-1, higher is better)

class SearchResponse(BaseModel):
    """Response from semantic search."""
    query: str
    results: List[SearchResult]
    total: int
```

### Pattern 3: Index Persistence
**What:** Save/load vector index for reuse

**When to use:** Avoid regenerating embeddings on every startup

**Example:**
```python
import numpy as np
import pickle

def save_index(index: NearestNeighbors, embeddings: np.ndarray, items: List[MediaItem], path: str):
    """Save index and metadata to disk."""
    with open(path, 'wb') as f:
        pickle.dump({
            'index': index,
            'embeddings': embeddings,
            'items': items  # Store item metadata for result construction
        }, f)

def load_index(path: str):
    """Load index from disk."""
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data['index'], data['embeddings'], data['items']
```

### Anti-Patterns to Avoid
- **Generating embeddings at query time for all items:** Pre-compute and cache embeddings
- **Using default model without consideration:** all-MiniLM-L6-v2 is fast (15ms/query) but consider larger models if quality is insufficient
- **Storing embeddings as float32 in JSON:** Use numpy binary format (.npy) or pickle
- **Ignoring cosine similarity:** Descriptions have varying lengths; cosine handles this better than euclidean

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text to vector conversion | Custom TF-IDF or word2vec | sentence-transformers | Pre-trained on massive corpora; captures semantic meaning not just keywords |
| Nearest neighbor search | Custom brute-force O(n*d) | sklearn NearestNeighbors | Optimized algorithms (ball_tree, KD-tree); handles cosine/euclidean |
| Model selection | Random selection | all-MiniLM-L6-v2 | Good balance of speed (15ms), dimension (384), quality (MTEB benchmark) |

**Key insight:** Semantic search is fundamentally about representation learning. Custom solutions cannot match pre-trained transformer models that have learned rich semantic representations from billions of text samples.

## Common Pitfalls

### Pitfall 1: Embedding Dimension Mismatch
**What goes wrong:** Index and query embeddings have different dimensions due to using different models
**Why it happens:** Model names hardcoded in multiple places; model changed without re-indexing
**How to avoid:** Store model name with index; validate dimensions on load
**Warning signs:** Shape mismatch errors, consistently poor search results

### Pitfall 2: Forgetting to Re-index After Dataset Changes
**What goes wrong:** New items added but index not rebuilt; new items never appear in results
**Why it happens:** Index built once, dataset modified without update
**How to avoid:** Build index as part of dataset loading; implement explicit rebuild method
**Warning signs:** Missing results for recently-added items

### Pitfall 3: Cosine Distance vs Cosine Similarity Confusion
**What goes wrong:** Returning distance as similarity (higher = better)
**Why it happens:** sklearn returns distances, not similarities; cosine distance = 1 - cosine similarity
**How to avoid:** Convert: similarity = 1 - distance
**Warning signs:** Results seem reversed (most "similar" shows highest score)

### Pitfall 4: Memory Issues with Large Embeddings
**What goes wrong:** Running out of memory when generating embeddings for large datasets
**Why it happens:** Loading all descriptions at once; not using batch processing
**How to avoid:** Use model.encode() with batch_size parameter; process in chunks
**Warning signs:** MemoryError during embedding generation

## Code Examples

### Complete Search Module Example
```python
"""Semantic search for media dataset."""

from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
from pathlib import Path
from typing import List, Optional
import pickle

from src.models.media import MediaDataset, MediaItem
from .search_result import SearchResult, SearchResponse


class SemanticSearch:
    """Semantic search over media descriptions."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize search with embedding model."""
        self.model = SentenceTransformer(model_name)
        self.index: Optional[NearestNeighbors] = None
        self.embeddings: Optional[np.ndarray] = None
        self.items: List[MediaItem] = []

    def build_index(self, dataset: MediaDataset) -> None:
        """Build search index from dataset."""
        self.items = dataset.items
        descriptions = [item.description for item in self.items]
        self.embeddings = self.model.encode(descriptions, show_progress_bar=True)
        self.index = NearestNeighbors(n_neighbors=len(self.items), metric='cosine')
        self.index.fit(self.embeddings)

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Search for media matching query."""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.kneighbors(query_embedding)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            item = self.items[idx]
            similarity = 1 - distance  # Convert distance to similarity
            results.append(SearchResult(
                id=item.id,
                path=item.path,
                description=item.description,
                media_type=item.media_type,
                format=item.format,
                score=round(similarity, 4)
            ))

        return SearchResponse(
            query=query,
            results=results[:top_k],
            total=len(results)
        )

    def save_index(self, path: str) -> None:
        """Persist index to disk."""
        with open(path, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'embeddings': self.embeddings,
                'items': self.items
            }, f)

    @classmethod
    def load_index(cls, path: str, model_name: str = "all-MiniLM-L6-v2") -> "SemanticSearch":
        """Load pre-built index from disk."""
        instance = cls(model_name)
        with open(path, 'rb') as f:
            data = pickle.load(f)
        instance.index = data['index']
        instance.embeddings = data['embeddings']
        instance.items = data['items']
        return instance
```

### Performance Notes (SRCH-04: < 2 seconds for 10K items)
```python
# For 10,000 items:
# - Embedding generation: ~30 seconds (one-time, batched)
# - Index building: < 1 second
# - Query time: ~50-100ms (sklearn NearestNeighbors)
#
# This meets SRCH-04 easily (2 second requirement)
#
# If using FAISS with IVF index:
# - Build: ~10 seconds
# - Query: ~10ms (but with ~5% accuracy loss)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| TF-IDF keyword matching | Sentence transformer embeddings | ~2020 | Captures semantic meaning, not just keywords |
| Exact nearest neighbor | Approximate nearest neighbor (ANN) | ~2015+ | Scales to billions with minimal accuracy loss |
| Single-model embeddings | Multi-model retrieval (MTEB leaderboard) | 2022+ | Task-specific models outperform general purpose |

**Deprecated/outdated:**
- **Word2Vec/FastText:** Outclassed by transformer-based models; only use for legacy compatibility
- **ElasticSearch vector search:** Originally keyword-only; still useful for hybrid but overkill for v1

## Open Questions

1. **Should we include categories/tags in embedding?**
   - What we know: Current design embeds description only
   - What's unclear: Whether adding categories/tags improves search quality
   - Recommendation: Start with description-only; add categories/tags if search quality is insufficient (ADV-01 deferred to v2)

2. **How to handle embedding model updates?**
   - What we know: Model weights can change; embeddings are not backwards compatible
   - What's unclear: How to manage model version in production
   - Recommendation: Store model name with index; rebuild on model change

3. **Should we support GPU for embedding generation?**
   - What we know: CUDA can speed up embedding by 10x
   - What's unclear: Whether GPU is available in target environment
   - Recommendation: Start with CPU; add GPU support if generation time is problematic (deferred)

## Validation Architecture

> Section added for Nyquist compliance (config: verification.nyquist_verify = true)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Python standard) |
| Config file | `pytest.ini` (existing in pyproject.toml) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SRCH-01 | Embedding model generates vectors from text | Unit | `pytest tests/test_embedder.py -k test_generate_embeddings -x` | Wave 0 |
| SRCH-02 | Vector index supports similarity search | Unit | `pytest tests/test_index.py -k test_build_and_search -x` | Wave 0 |
| SRCH-03 | Search returns top N ranked results with scores | Unit | `pytest tests/test_search.py -k test_search_returns_ranked -x` | Wave 0 |
| SRCH-04 | Query response under 2 seconds for 10K items | Performance | `pytest tests/test_search.py -k test_performance_under_2s -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** Run affected test files only (`pytest tests/test_<module>.py -x -q`)
- **Per wave merge:** Run full test suite (`pytest tests/ -v`)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_embedder.py` — covers SRCH-01 (embedding generation)
- [ ] `tests/test_index.py` — covers SRCH-02 (vector index)
- [ ] `tests/test_search.py` — covers SRCH-03 (ranked results), SRCH-04 (performance)
- [ ] `tests/conftest.py` — add fixtures for SemanticSearch, sample embeddings
- [ ] Framework install: `pip install sentence-transformers scikit-learn numpy torch` — if not in dependencies

*(Note: No search implementation code exists yet — all test files are Wave 0 gaps)*

## Sources

### Primary (HIGH confidence)
- [sbert.net](https://sbert.net/) - sentence-transformers installation and usage
- [FAISS.ai](https://faiss.ai/) - vector similarity search library
- [scikit-learn NearestNeighbors](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html) - sklearn vector search
- [docs.trychroma.com](https://docs.trychroma.com/) - Chroma embedding database

### Secondary (MEDIUM confidence)
- [Hugging Face MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - embedding model benchmarks

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - sentence-transformers and sklearn are well-established
- Architecture: HIGH - pattern follows industry best practices
- Pitfalls: HIGH - documented from real-world experience

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (30 days - embedding libraries stable)

---

*Phase: 02-semantic-search-core*
*Research gathered: 2026-03-15*
