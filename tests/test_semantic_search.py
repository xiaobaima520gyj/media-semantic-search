"""Tests for SemanticSearch high-level API."""

import pytest

from src.search.embedder import Embedder
from src.search.semantic_search import SemanticSearch
from src.models.media import MediaDataset


class TestSemanticSearch:
    """Test cases for the SemanticSearch API."""

    @pytest.fixture
    def sample_dataset(self) -> MediaDataset:
        """Create a small sample dataset for testing."""
        return MediaDataset(items=[
            {'id': '1', 'path': 'a.jpg', 'description': 'A cat sleeping on windowsill', 'media_type': 'image', 'format': 'jpg'},
            {'id': '2', 'path': 'b.jpg', 'description': 'A dog running in park', 'media_type': 'image', 'format': 'jpg'},
            {'id': '3', 'path': 'c.jpg', 'description': 'Sunset over ocean', 'media_type': 'image', 'format': 'jpg'}
        ])

    def test_search_returns_search_response(self, sample_dataset):
        """Test that search() returns a SearchResponse object."""
        search = SemanticSearch()
        search.build_index(sample_dataset)
        result = search.search('kitten on windowsill', top_k=2)

        # Should have query, results, and total
        assert result.query == 'kitten on windowsill'
        assert hasattr(result, 'results')
        assert hasattr(result, 'total')

    def test_search_results_have_required_fields(self, sample_dataset):
        """Test that search results contain path, description, and score."""
        search = SemanticSearch()
        search.build_index(sample_dataset)
        result = search.search('sleeping cat', top_k=3)

        assert len(result.results) > 0
        first_result = result.results[0]
        assert hasattr(first_result, 'path')
        assert hasattr(first_result, 'description')
        assert hasattr(first_result, 'score')

    def test_search_results_sorted_by_score_descending(self, sample_dataset):
        """Test that results are sorted by score descending (highest relevance first)."""
        search = SemanticSearch()
        search.build_index(sample_dataset)
        result = search.search('sleeping cat', top_k=3)

        if len(result.results) >= 2:
            # Check that scores are in descending order
            scores = [r.score for r in result.results]
            assert scores == sorted(scores, reverse=True), f"Scores should be sorted descending: {scores}"

    def test_top_k_parameter_limits_results(self, sample_dataset):
        """Test that top_k parameter correctly limits the number of results."""
        search = SemanticSearch()
        search.build_index(sample_dataset)

        # Request top 2
        result_2 = search.search('cat', top_k=2)
        assert len(result_2.results) == 2

        # Request top 1
        result_1 = search.search('cat', top_k=1)
        assert len(result_1.results) == 1

    def test_search_handles_empty_index(self):
        """Test that search handles an empty index gracefully."""
        search = SemanticSearch()
        # Build with empty dataset
        empty_dataset = MediaDataset(items=[])
        search.build_index(empty_dataset)

        result = search.search('test query', top_k=5)
        assert len(result.results) == 0
        assert result.total == 0

    def test_search_handles_top_k_exceeds_available(self, sample_dataset):
        """Test that search handles top_k greater than available results."""
        search = SemanticSearch()
        search.build_index(sample_dataset)

        # Request more than available
        result = search.search('cat', top_k=100)
        # Should return all available results
        assert len(result.results) <= len(sample_dataset.items)
