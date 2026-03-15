"""Tests for the VectorIndex module."""

import numpy as np
import pytest
from pathlib import Path
import tempfile
import os

from src.search.embedder import Embedder
from src.search.index import VectorIndex
from src.models.media import MediaDataset


class TestVectorIndex:
    """Test suite for VectorIndex class."""

    @pytest.fixture
    def embedder(self):
        """Create an embedder instance for testing."""
        return Embedder()

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset for testing."""
        return MediaDataset(items=[
            {
                'id': '1',
                'path': 'images/cat.jpg',
                'description': 'A cat sleeping on a windowsill',
                'media_type': 'image',
                'format': 'jpg'
            },
            {
                'id': '2',
                'path': 'videos/dog.mp4',
                'description': 'A dog running in the park',
                'media_type': 'video',
                'format': 'mp4'
            },
            {
                'id': '3',
                'path': 'images/mountain.jpg',
                'description': 'Mountain sunrise with clouds',
                'media_type': 'image',
                'format': 'jpg'
            },
            {
                'id': '4',
                'path': 'images/city.jpg',
                'description': 'City night skyline with lights',
                'media_type': 'image',
                'format': 'jpg'
            },
            {
                'id': '5',
                'path': 'videos/ocean.mp4',
                'description': 'Ocean waves crashing on beach',
                'media_type': 'video',
                'format': 'mp4'
            }
        ])

    def test_build_index_creates_nearest_neighbors_index(self, embedder, sample_dataset):
        """Test that build_index creates a NearestNeighbors index."""
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        # Verify the index is built
        assert index._index is not None
        assert hasattr(index._index, 'kneighbors')

    def test_search_returns_indices_and_distances(self, embedder, sample_dataset):
        """Test that search returns indices and distances."""
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        # Search for a sleeping pet
        query_embedding = embedder.embed('a sleeping pet')
        distances, indices = index.search(query_embedding, top_k=3)

        # Verify shapes
        assert indices.shape[0] == 1
        assert indices.shape[1] == 3
        assert distances.shape[0] == 1
        assert distances.shape[1] == 3

        # Verify indices are valid
        assert np.all(indices >= 0)
        assert np.all(indices < len(sample_dataset.items))

    def test_distances_are_cosine_distance(self, embedder, sample_dataset):
        """Test that distances are cosine distance (0-2 range for normalized vectors).

        Cosine distance = 1 - cosine_similarity
        For normalized vectors, cosine_similarity = dot product in [-1, 1]
        Therefore cosine distance is in [0, 2]
        """
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        query_embedding = embedder.embed('test query')
        distances, indices = index.search(query_embedding, top_k=5)

        # Cosine distance should be between 0 and 2
        # 0 = identical vectors, 2 = opposite directions
        assert np.all(distances >= 0)
        assert np.all(distances <= 2)

    def test_similarity_conversion(self, embedder, sample_dataset):
        """Test that similarity = 1 - distance."""
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        query_embedding = embedder.embed('test query')
        distances, indices = index.search(query_embedding, top_k=5)

        # Convert to similarity
        similarities = 1 - distances

        # Similarity is in [-1, 1] for normalized vectors
        # 1 = identical, 0 = orthogonal, -1 = opposite
        assert np.all(similarities >= -1)
        assert np.all(similarities <= 1)

    def test_empty_dataset_handling(self, embedder):
        """Test handling of empty dataset."""
        empty_dataset = MediaDataset(items=[])

        index = VectorIndex(embedder)
        index.build_index(empty_dataset)

        # Search should handle empty index gracefully
        query_embedding = embedder.embed('test')
        distances, indices = index.search(query_embedding, top_k=5)

        # Should return empty results
        assert indices.shape[1] == 0

    def test_top_k_larger_than_dataset(self, embedder, sample_dataset):
        """Test handling when top_k > dataset size."""
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        query_embedding = embedder.embed('test query')
        # Request more than dataset size
        distances, indices = index.search(query_embedding, top_k=100)

        # Should return all available items
        assert indices.shape[1] == len(sample_dataset.items)

    def test_save_and_load_index(self, embedder, sample_dataset):
        """Test that index can be saved and loaded from disk."""
        index = VectorIndex(embedder)
        index.build_index(sample_dataset)

        # Save to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, 'test_index.pkl')
            index.save_index(index_path)

            # Verify file exists
            assert os.path.exists(index_path)

            # Load the index
            loaded_index = VectorIndex.load_index(index_path, embedder)

            # Verify loaded index works
            query_embedding = embedder.embed('a sleeping pet')
            distances, indices = loaded_index.search(query_embedding, top_k=3)

            # Should return same results
            assert indices.shape == (1, 3)


class TestVectorIndexIntegration:
    """Integration tests for VectorIndex with real embeddings."""

    @pytest.fixture
    def embedder(self):
        """Create an embedder instance."""
        return Embedder()

    def test_semantic_search_finds_similar(self, embedder):
        """Test that semantic search finds conceptually similar items."""
        # Create dataset with distinct categories
        dataset = MediaDataset(items=[
            {'id': '1', 'path': 'a.jpg', 'description': 'A cat sleeping', 'media_type': 'image', 'format': 'jpg'},
            {'id': '2', 'path': 'b.jpg', 'description': 'A dog running', 'media_type': 'image', 'format': 'jpg'},
            {'id': '3', 'path': 'c.jpg', 'description': 'Mountain landscape', 'media_type': 'image', 'format': 'jpg'},
        ])

        index = VectorIndex(embedder)
        index.build_index(dataset)

        # Search for cat-like content
        query_embedding = embedder.embed('a sleeping pet')
        distances, indices = index.search(query_embedding, top_k=2)

        # The "cat" item should be the top result (index 0)
        # and "dog" should be second (index 1)
        # since "sleeping pet" is closer to "cat" than to "dog" or "mountain"
        assert indices[0][0] == 0  # cat should be top match

    def test_search_with_different_top_k(self, embedder):
        """Test search with varying top_k values."""
        dataset = MediaDataset(items=[
            {'id': str(i), 'path': f'img{i}.jpg', 'description': f'Description {i}',
             'media_type': 'image', 'format': 'jpg'}
            for i in range(10)
        ])

        index = VectorIndex(embedder)
        index.build_index(dataset)

        query_embedding = embedder.embed('test')

        # Test different top_k values
        for k in [1, 3, 5, 10]:
            distances, indices = index.search(query_embedding, top_k=k)
            assert indices.shape[1] == k
