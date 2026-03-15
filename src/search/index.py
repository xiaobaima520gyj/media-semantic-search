"""Vector index module for semantic similarity search using sklearn NearestNeighbors."""

import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors

from src.models.media import MediaDataset, MediaItem
from .embedder import Embedder


class VectorIndex:
    """Vector index for semantic similarity search over media descriptions.

    Uses sklearn NearestNeighbors with cosine metric to find similar items
    based on their text descriptions converted to embeddings.
    """

    def __init__(self, embedder: Embedder):
        """Initialize the vector index with an embedder.

        Args:
            embedder: An Embedder instance to convert text to embeddings.
        """
        self._embedder = embedder
        self._index: Optional[NearestNeighbors] = None
        self._embeddings: Optional[np.ndarray] = None
        self._items: List[MediaItem] = []
        self._model_name: str = embedder.model_name

    def build_index(self, dataset: MediaDataset) -> None:
        """Build the search index from a media dataset.

        Generates embeddings for all item descriptions and fits the
        NearestNeighbors index.

        Args:
            dataset: A MediaDataset containing items to index.
        """
        self._items = dataset.items

        if len(self._items) == 0:
            # Handle empty dataset
            self._embeddings = np.array([])
            self._index = None
            return

        # Extract descriptions and generate embeddings
        descriptions = [item.description for item in self._items]
        self._embeddings = self._embedder.embed_batch(descriptions)

        # Normalize embeddings to unit length for reliable cosine distance in [0, 1]
        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        self._embeddings = self._embeddings / norms

        # Build NearestNeighbors index with cosine metric
        # n_neighbors is set to dataset size to allow querying all items
        n_neighbors = min(len(self._items), len(self._items))
        self._index = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='auto'
        )
        self._index.fit(self._embeddings)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for the most similar items to a query embedding.

        Args:
            query_embedding: The embedding vector to search for.
            top_k: Number of results to return.

        Returns:
            A tuple (distances, indices) where:
            - distances: Array of cosine distances (shape: (1, top_k))
            - indices: Array of indices into the items list (shape: (1, top_k))

            Note: Cosine distance = 1 - cosine similarity.
            To convert to similarity: similarity = 1 - distance
        """
        if self._index is None or len(self._items) == 0:
            # Return empty results for empty index
            empty_indices = np.array([[]]).astype(int)
            empty_distances = np.array([[]]).astype(float)
            return empty_distances, empty_indices

        # Ensure query is 2D (1, embedding_dim)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Normalize query embedding to unit length for reliable cosine distance
        query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        query_norm = np.where(query_norm == 0, 1, query_norm)
        query_embedding = query_embedding / query_norm

        # Adjust top_k if it exceeds dataset size
        actual_k = min(top_k, len(self._items))

        # Re-fit index with correct n_neighbors if needed
        if self._index.n_neighbors != actual_k:
            self._index = NearestNeighbors(
                n_neighbors=actual_k,
                metric='cosine',
                algorithm='auto'
            )
            self._index.fit(self._embeddings)

        # Search the index
        distances, indices = self._index.kneighbors(query_embedding, n_neighbors=actual_k)

        return distances, indices

    def save_index(self, path: str) -> None:
        """Save the index and associated data to disk.

        Saves the NearestNeighbors index, embeddings, items, and model name
        to a pickle file.

        Args:
            path: Path where the index should be saved.
        """
        data = {
            'index': self._index,
            'embeddings': self._embeddings,
            'items': self._items,
            'model_name': self._model_name
        }

        file_path = Path(path)
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

    @classmethod
    def load_index(cls, path: str, embedder: Embedder) -> "VectorIndex":
        """Load a previously saved index from disk.

        Args:
            path: Path to the saved index file.
            embedder: An Embedder instance (used for embedding dimension validation).

        Returns:
            A VectorIndex instance with the loaded data.
        """
        file_path = Path(path)
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        instance = cls(embedder)
        instance._index = data['index']
        instance._embeddings = data['embeddings']
        instance._items = data['items']
        instance._model_name = data.get('model_name', embedder.model_name)

        return instance

    @property
    def items(self) -> List[MediaItem]:
        """Return the list of indexed items."""
        return self._items

    @property
    def is_built(self) -> bool:
        """Return whether the index has been built."""
        return self._index is not None


# Module-level convenience functions

def build_index(dataset: MediaDataset, embedder: Embedder) -> VectorIndex:
    """Build a vector index from a dataset.

    Args:
        dataset: The MediaDataset to index.
        embedder: The Embedder to use for generating embeddings.

    Returns:
        A VectorIndex instance with the built index.
    """
    index = VectorIndex(embedder)
    index.build_index(dataset)
    return index


def save_index(index: VectorIndex, path: str) -> None:
    """Save a vector index to disk.

    Args:
        index: The VectorIndex to save.
        path: Path where the index should be saved.
    """
    index.save_index(path)


def load_index(path: str, embedder: Embedder) -> VectorIndex:
    """Load a vector index from disk.

    Args:
        path: Path to the saved index file.
        embedder: An Embedder instance.

    Returns:
        A VectorIndex instance with the loaded index.
    """
    return VectorIndex.load_index(path, embedder)
