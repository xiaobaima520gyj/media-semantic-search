"""Semantic search module for multimedia retrieval."""

from src.search.embedder import Embedder, DEFAULT_MODEL
from src.search.index import VectorIndex, build_index, save_index, load_index

__all__ = ["Embedder", "DEFAULT_MODEL", "VectorIndex", "build_index", "save_index", "load_index"]
