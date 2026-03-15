"""High-level SemanticSearch API combining embedder and vector index."""

from typing import List, Optional
from pathlib import Path

from src.models.media import MediaDataset, MediaItem
from src.search.embedder import Embedder, DEFAULT_MODEL
from src.search.index import VectorIndex
from src.search.search_result import SearchResult, SearchResponse


class SemanticSearch:
    """High-level semantic search API combining embedder and vector index.

    Provides a simple interface for building search indexes from media datasets
    and performing semantic similarity searches. Combines the Embedder (for
    text-to-vector conversion) and VectorIndex (for similarity search) into
    a single unified API.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the semantic search with an embedding model.

        Args:
            model_name: Name of the sentence-transformers model to use.
                        Defaults to 'all-MiniLM-L6-v2' which produces 384-dim vectors.
        """
        self._embedder: Optional[Embedder] = None
        self._index: Optional[VectorIndex] = None
        self._model_name = model_name
        self._lazy_load()

    def _lazy_load(self) -> None:
        """Lazily initialize the embedder on first use."""
        if self._embedder is None:
            self._embedder = Embedder(self._model_name)
            self._index = VectorIndex(self._embedder)

    @property
    def embedder(self) -> Embedder:
        """Return the embedder instance."""
        self._lazy_load()
        return self._embedder

    @property
    def index(self) -> VectorIndex:
        """Return the vector index instance."""
        self._lazy_load()
        return self._index

    @property
    def is_built(self) -> bool:
        """Return whether the index has been built."""
        return self._index is not None and self._index.is_built

    def build_index(self, dataset: MediaDataset) -> None:
        """Build the search index from a media dataset.

        Generates embeddings for all item descriptions and builds the
        vector index for similarity search.

        Args:
            dataset: A MediaDataset containing items to index.
        """
        self._lazy_load()
        self._index.build_index(dataset)

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Search for media items matching the query.

        Embeds the query text, searches the index for nearest neighbors,
        and returns ranked results with similarity scores.

        Args:
            query: The search query text.
            top_k: Maximum number of results to return. Defaults to 5.

        Returns:
            A SearchResponse containing the query, ranked results, and total count.
        """
        if self._index is None or not self._index.is_built:
            # Return empty response if index not built
            return SearchResponse(
                query=query,
                results=[],
                total=0
            )

        # Embed the query text
        query_embedding = self._embedder.embed(query)

        # Search the index for nearest neighbors
        distances, indices = self._index.search(query_embedding, top_k=top_k)

        # Convert distances to similarity scores (1 - distance)
        # Distance is cosine distance, so similarity = 1 - distance
        # This gives a score in [0, 1] range (0 = not similar, 1 = identical)
        similarities = 1 - distances[0]

        # Build SearchResult objects
        items = self._index.items
        results: List[SearchResult] = []

        for idx, sim_score in zip(indices[0], similarities):
            if idx < len(items):
                item = items[idx]
                results.append(SearchResult(
                    id=item.id,
                    path=item.path,
                    description=item.description,
                    media_type=item.media_type,
                    format=item.format,
                    score=round(float(sim_score), 4)
                ))

        # Limit results to top_k
        results = results[:top_k]

        return SearchResponse(
            query=query,
            results=results,
            total=len(items)
        )

    def save_index(self, path: str) -> None:
        """Save the search index to disk.

        Saves the vector index, embeddings, and associated data to
        a pickle file for later reuse.

        Args:
            path: Path where the index should be saved.
        """
        if self._index is not None:
            self._index.save_index(path)

    @classmethod
    def load_index(cls, path: str, model_name: str = DEFAULT_MODEL) -> "SemanticSearch":
        """Load a pre-built search index from disk.

        Args:
            path: Path to the saved index file.
            model_name: Name of the embedding model (for validation).

        Returns:
            A SemanticSearch instance with the loaded index.
        """
        instance = cls(model_name)
        instance._lazy_load()
        instance._index = VectorIndex.load_index(path, instance._embedder)
        return instance

    def __len__(self) -> int:
        """Return the number of items in the index."""
        if self._index is not None and self._index.is_built:
            return len(self._index.items)
        return 0
