"""Unit tests for the Python API."""

import json
from pathlib import Path

import pytest

from src.api import MediaSearch


@pytest.fixture
def sample_dataset(tmp_path):
    """Create a temporary sample dataset for testing."""
    data = {
        "version": "1.0",
        "items": [
            {
                "id": "img-001",
                "path": "images/cat.jpg",
                "description": "A cute orange cat sitting on a windowsill",
                "media_type": "image",
                "format": "jpg",
                "categories": ["animals", "cats"],
                "tags": ["cute", "orange", "indoor"]
            },
            {
                "id": "img-002",
                "path": "images/dog.jpg",
                "description": "A golden retriever playing in the park",
                "media_type": "image",
                "format": "jpg",
                "categories": ["animals", "dogs"],
                "tags": ["dog", "park", "playing"]
            },
            {
                "id": "img-003",
                "path": "videos/beach.mp4",
                "description": "Sunset over the beach with waves",
                "media_type": "video",
                "format": "mp4",
                "categories": ["nature", "beach"],
                "tags": ["sunset", "ocean", "waves"]
            }
        ]
    }
    dataset_file = tmp_path / "dataset.json"
    with open(dataset_file, "w") as f:
        json.dump(data, f)
    return str(dataset_file)


def test_media_search_api_import():
    """Test that MediaSearch can be imported."""
    from src.api import MediaSearch
    assert MediaSearch is not None


def test_media_search_instantiation(sample_dataset):
    """Test MediaSearch can be instantiated with a dataset path."""
    search = MediaSearch(sample_dataset)
    assert search is not None
    assert search.dataset is not None
    assert len(search.dataset.items) == 3


def test_media_search_query_returns_results(sample_dataset):
    """Test that search.query() returns a list of SearchResult."""
    search = MediaSearch(sample_dataset)
    results = search.query("cat", top_k=2)

    assert isinstance(results, list)
    assert len(results) <= 2


def test_search_result_fields(sample_dataset):
    """Test that SearchResult has all required fields."""
    search = MediaSearch(sample_dataset)
    results = search.query("animal", top_k=1)

    assert len(results) > 0
    r = results[0]

    # Required fields from API-03
    assert hasattr(r, 'path')
    assert hasattr(r, 'score')
    assert hasattr(r, 'description')
    assert hasattr(r, 'media_type')
    assert hasattr(r, 'format')

    # Verify types
    assert isinstance(r.path, str)
    assert isinstance(r.score, float)
    assert 0.0 <= r.score <= 1.0
    assert isinstance(r.description, str)
    assert r.media_type in ("image", "video")
    assert isinstance(r.format, str)


def test_search_result_path_format(sample_dataset):
    """Test that result path is the relative path from dataset."""
    search = MediaSearch(sample_dataset)
    results = search.query("cat", top_k=1)

    assert len(results) > 0
    # Path should be relative (as stored in dataset)
    assert "cat.jpg" in results[0].path or results[0].path.endswith(".jpg")
