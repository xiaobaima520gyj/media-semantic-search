"""Test fixtures for validators."""

import json
import os
import tempfile
from datetime import datetime
from typing import List

from src.models.media import MediaDataset, MediaItem


def create_sample_item(
    item_id: str = "test_001",
    path: str = "images/test.jpg",
    description: str = "A test image",
    media_type: str = "image",
    format_str: str = "jpg",
    categories: List[str] = None,
    tags: List[str] = None,
) -> MediaItem:
    """Create a sample MediaItem for testing."""
    return MediaItem(
        id=item_id,
        path=path,
        description=description,
        media_type=media_type,
        format=format_str,
        categories=categories or [],
        tags=tags or [],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def create_sample_dataset(items: List[MediaItem] = None) -> MediaDataset:
    """Create a sample MediaDataset for testing."""
    return MediaDataset(
        version="1.0",
        items=items or [create_sample_item()],
    )


def create_temp_dataset_file(items: List[MediaItem] = None) -> str:
    """Create a temporary dataset JSON file."""
    dataset = create_sample_dataset(items)
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    dataset.save(path)
    return path
