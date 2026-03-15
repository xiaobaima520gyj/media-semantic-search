"""Tests for search result models."""

import pytest
from src.search.search_result import SearchResult, SearchResponse


class TestSearchResult:
    """Test cases for SearchResult model."""

    def test_search_result_has_required_fields(self):
        """Test that SearchResult has all required fields."""
        result = SearchResult(
            id="test_001",
            path="images/cat.jpg",
            description="A sleeping cat",
            media_type="image",
            format="jpg",
            score=0.95
        )
        assert result.id == "test_001"
        assert result.path == "images/cat.jpg"
        assert result.description == "A sleeping cat"
        assert result.media_type == "image"
        assert result.format == "jpg"
        assert result.score == 0.95

    def test_search_result_score_is_float(self):
        """Test that score is stored as float."""
        result = SearchResult(
            id="test_001",
            path="images/test.jpg",
            description="Test",
            media_type="image",
            format="jpg",
            score=0.95
        )
        assert isinstance(result.score, float)

    def test_search_result_model_dump(self):
        """Test that SearchResult can be serialized to dict."""
        result = SearchResult(
            id="test_001",
            path="images/test.jpg",
            description="Test description",
            media_type="image",
            format="jpg",
            score=0.85
        )
        data = result.model_dump()
        assert data["id"] == "test_001"
        assert data["score"] == 0.85

    def test_search_result_video_type(self):
        """Test that SearchResult works with video media_type."""
        result = SearchResult(
            id="vid_001",
            path="videos/clip.mp4",
            description="A video clip",
            media_type="video",
            format="mp4",
            score=0.9
        )
        assert result.media_type == "video"
        assert result.format == "mp4"


class TestSearchResponse:
    """Test cases for SearchResponse model."""

    def test_search_response_has_required_fields(self):
        """Test that SearchResponse has query, results, and total."""
        results = [
            SearchResult(
                id="test_001",
                path="images/cat.jpg",
                description="A cat",
                media_type="image",
                format="jpg",
                score=0.95
            ),
            SearchResult(
                id="test_002",
                path="images/dog.jpg",
                description="A dog",
                media_type="image",
                format="jpg",
                score=0.85
            )
        ]
        response = SearchResponse(
            query="pet animal",
            results=results,
            total=2
        )
        assert response.query == "pet animal"
        assert len(response.results) == 2
        assert response.total == 2

    def test_search_response_with_empty_results(self):
        """Test that SearchResponse works with empty results."""
        response = SearchResponse(
            query="nonexistent",
            results=[],
            total=0
        )
        assert response.query == "nonexistent"
        assert len(response.results) == 0
        assert response.total == 0

    def test_search_response_model_dump(self):
        """Test that SearchResponse can be serialized to dict."""
        results = [
            SearchResult(
                id="test_001",
                path="images/test.jpg",
                description="Test",
                media_type="image",
                format="jpg",
                score=0.9
            )
        ]
        response = SearchResponse(
            query="test query",
            results=results,
            total=1
        )
        data = response.model_dump()
        assert data["query"] == "test query"
        assert len(data["results"]) == 1
        assert data["total"] == 1
