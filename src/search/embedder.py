"""Embedding module for semantic search using sentence-transformers."""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


# Default embedding model - all-MiniLM-L6-v2 produces 384-dimensional vectors
DEFAULT_MODEL = "all-MiniLM-L6-v2"


class Embedder:
    """Wrapper for sentence-transformers embedding model."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the embedder with a sentence-transformers model.

        Args:
            model_name: Name of the sentence-transformers model to use.
                        Defaults to 'all-MiniLM-L6-v2' which produces 384-dim vectors.
        """
        self._model = SentenceTransformer(model_name)
        self._model_name = model_name
        # Get embedding dimension from the model
        self._embedding_dim = self._model.get_sentence_embedding_dimension()

    @property
    def embedding_dim(self) -> int:
        """Return the dimensionality of the embedding vectors."""
        return self._embedding_dim

    @property
    def model_name(self) -> str:
        """Return the name of the model being used."""
        return self._model_name

    def embed(self, text: str) -> np.ndarray:
        """Convert a single text string to a vector embedding.

        Args:
            text: The text to embed.

        Returns:
            numpy array of shape (embedding_dim,) containing the embedding vector.
        """
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Convert multiple text strings to vector embeddings in batch.

        Args:
            texts: List of texts to embed.

        Returns:
            numpy array of shape (len(texts), embedding_dim) containing embedding vectors.
        """
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings
