"""Tests for the Embedder module (SRCH-01)."""

import numpy as np
import pytest
from src.search.embedder import Embedder, DEFAULT_MODEL


class TestEmbedder:
    """Test cases for the Embedder class."""

    def test_default_model_is_minilm(self):
        """Test that default model is all-MiniLM-L6-v2."""
        assert DEFAULT_MODEL == "all-MiniLM-L6-v2"

    def test_embed_returns_384_dimensions(self):
        """Test that embed() returns numpy array of shape (384,)."""
        embedder = Embedder()
        result = embedder.embed("a sleeping cat")
        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)

    def test_embed_batch_returns_correct_shape(self):
        """Test that embed_batch() returns array of shape (2, 384)."""
        embedder = Embedder()
        result = embedder.embed_batch(["cat", "dog"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 384)

    def test_embed_batch_single_item(self):
        """Test that embed_batch() works with single item."""
        embedder = Embedder()
        result = embedder.embed_batch(["cat"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 384)

    def test_embed_dimensions_property(self):
        """Test that embedding_dim property returns 384."""
        embedder = Embedder()
        assert embedder.embedding_dim == 384

    def test_embed_returns_float_array(self):
        """Test that embeddings are float values."""
        embedder = Embedder()
        result = embedder.embed("test text")
        assert result.dtype == np.float32 or result.dtype == np.float64
