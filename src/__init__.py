"""Multimedia Dataset Retrieval System.

A semantic search system for finding images and videos by natural language queries.

Example:
    from src import MediaSearch, SemanticSearch, MediaDataset

    # Simple one-line search
    search = MediaSearch("data/dataset.json")
    results = search.query("cats on windowsill", top_k=10)

    # Low-level API
    dataset = MediaDataset.load("data/dataset.json")
    search_engine = SemanticSearch()
    search_engine.build_index(dataset)
    results = search_engine.search("query")
"""

from src.api import MediaSearch
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
