"""Performance tests for semantic search - verifies SRCH-04 requirement."""

import time
import pytest
from unittest.mock import Mock, patch

from src.search.semantic_search import SemanticSearch
from src.models.media import MediaDataset, MediaItem


def generate_mock_embeddings(num_items: int, embedding_dim: int = 384):
    """Generate random mock embeddings for performance testing.

    This avoids actual embedding generation which is slow.
    """
    import numpy as np
    # Generate random embeddings and normalize them
    embeddings = np.random.randn(num_items, embedding_dim).astype(np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings


@pytest.mark.timeout(300)  # 5 minute timeout for entire test (including build)
class TestSearchPerformance:
    """Performance tests to verify SRCH-04: search under 2 seconds for 10K items."""

    def test_search_performance_under_2s(self):
        """Test that search completes in under 2 seconds for 10K items.

        SRCH-04: Search response time must be under 2 seconds for datasets
        up to 10,000 items.

        Note: Index building takes ~30 seconds for 10K items (expected),
        but search should be < 2s.
        """
        # Create 10K mock media items
        num_items = 10000
        items = []
        for i in range(num_items):
            items.append(MediaItem(
                id=f"item_{i}",
                path=f"media/item_{i}.jpg",
                description=f"Test media description {i}",
                media_type="image",
                format="jpg"
            ))

        dataset = MediaDataset(items=items)

        # Create SemanticSearch and build index
        search = SemanticSearch()

        # Measure index building time (informational only)
        build_start = time.time()
        search.build_index(dataset)
        build_time = time.time() - build_start
        print(f"\nIndex build time for {num_items} items: {build_time:.2f}s")

        # Verify index was built
        assert len(search) == num_items, f"Expected {num_items} items in index"

        # Measure search time - this is what SRCH-04 requires
        search_start = time.time()
        result = search.search("test query for semantic search", top_k=10)
        search_time = time.time() - search_start

        print(f"Search time for {num_items} items with top_k=10: {search_time:.3f}s")
        print(f"Number of results: {len(result.results)}")

        # SRCH-04: Search must be under 2 seconds
        assert search_time < 2.0, f"Search took {search_time:.3f}s, must be under 2s"

        # Verify results are returned
        assert len(result.results) == 10, "Should return top 10 results"

    def test_search_performance_scales_linearly(self):
        """Test that search time scales reasonably with dataset size.

        Verify that doubling the dataset doesn't cause exponential growth.
        """
        # Test with smaller sizes to verify scaling
        sizes = [1000, 5000]

        for size in sizes:
            items = [
                MediaItem(
                    id=f"item_{i}",
                    path=f"media/item_{i}.jpg",
                    description=f"Test description {i}",
                    media_type="image",
                    format="jpg"
                )
                for i in range(size)
            ]

            dataset = MediaDataset(items=items)
            search = SemanticSearch()
            search.build_index(dataset)

            # Measure search time
            start = time.time()
            result = search.search("test query", top_k=10)
            elapsed = time.time() - start

            print(f"\nSearch time for {size} items: {elapsed:.3f}s")

            # Should still be fast even for 5K items
            assert elapsed < 1.0, f"Search for {size} items took {elapsed:.3f}s"

    def test_empty_index_search_is_fast(self):
        """Test that searching empty index returns quickly."""
        dataset = MediaDataset(items=[])
        search = SemanticSearch()
        search.build_index(dataset)

        start = time.time()
        result = search.search("test query", top_k=10)
        elapsed = time.time() - start

        assert elapsed < 0.1, "Empty index search should be instant"
        assert len(result.results) == 0

    def test_top_k_affects_performance_minimally(self):
        """Test that increasing top_k doesn't significantly impact search time."""
        # Create moderate-sized dataset
        items = [
            MediaItem(
                id=f"item_{i}",
                path=f"media/item_{i}.jpg",
                description=f"Description {i}",
                media_type="image",
                format="jpg"
            )
            for i in range(5000)
        ]

        dataset = MediaDataset(items=items)
        search = SemanticSearch()
        search.build_index(dataset)

        # Test with different top_k values
        top_k_values = [5, 10, 50, 100]

        for top_k in top_k_values:
            start = time.time()
            result = search.search("test query", top_k=top_k)
            elapsed = time.time() - start

            print(f"\ntop_k={top_k}: {elapsed:.3f}s")

            # All should be under 2 seconds regardless of top_k
            assert elapsed < 2.0, f"Search with top_k={top_k} took {elapsed:.3f}s"
