"""Tests for dataset validators."""

import os
import tempfile

from src.models.media import MediaDataset, MediaItem
from src.validators.dataset_validator import (
    validate_dataset,
    validate_media_type_matches_format,
    validate_no_duplicates,
)


def test_valid_dataset_passes():
    """Test that a valid dataset passes validation."""
    items = [
        MediaItem(
            id="img_001",
            path="sample/images/cat.jpg",
            description="A test image",
            media_type="image",
            format="jpg",
            categories=["test"],
            tags=["test"],
        ),
    ]
    dataset = MediaDataset(version="1.0", items=items)

    # Save to temp file
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    dataset.save(path)

    try:
        # Validate with file check skipped (no actual files)
        result = validate_dataset(path, skip_file_check=True)
        assert result.is_valid, "Valid dataset should pass validation"
    finally:
        os.unlink(path)


def test_duplicate_ids_detected():
    """Test that duplicate IDs are detected."""
    items = [
        MediaItem(
            id="dup_id",
            path="images/test1.jpg",
            description="Test image 1",
            media_type="image",
            format="jpg",
        ),
        MediaItem(
            id="dup_id",
            path="images/test2.jpg",
            description="Test image 2",
            media_type="image",
            format="jpg",
        ),
    ]
    result = validate_no_duplicates(items)
    assert not result.is_valid, "Duplicate IDs should fail validation"
    assert any("dup_id" in e.message for e in result.errors), "Error should mention duplicate ID"


def test_duplicate_paths_detected():
    """Test that duplicate paths are detected."""
    items = [
        MediaItem(
            id="img_001",
            path="images/same_path.jpg",
            description="Test image 1",
            media_type="image",
            format="jpg",
        ),
        MediaItem(
            id="img_002",
            path="images/same_path.jpg",
            description="Test image 2",
            media_type="image",
            format="jpg",
        ),
    ]
    result = validate_no_duplicates(items)
    assert not result.is_valid, "Duplicate paths should fail validation"
    assert any("same_path.jpg" in e.message for e in result.errors), "Error should mention duplicate path"


def test_media_type_mismatch_detected():
    """Test that media_type/format mismatches are detected in JSON input.

    Note: Direct Pydantic model creation already validates this,
    so we test by loading from JSON which bypasses model validation.
    """
    import json

    # Create a dataset with mismatched media_type/format in JSON
    dataset_json = {
        "version": "1.0",
        "items": [
            {
                "id": "vid_001",
                "path": "videos/test.mp4",
                "description": "A video file",
                "media_type": "image",  # Wrong - should be video
                "format": "mp4",
            }
        ]
    }

    # Write to temp file and load
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w") as f:
        json.dump(dataset_json, f)

    try:
        # Load via MediaDataset (which applies validation)
        # The model validator will catch this
        from pydantic import ValidationError
        try:
            dataset = MediaDataset.load(path)
            # If we get here without exception, check with our validator
            result = validate_media_type_matches_format(dataset.items)
            assert not result.is_valid, "Media type mismatch should fail validation"
        except ValidationError as e:
            # Pydantic catches this at model level - also valid
            assert "media_type" in str(e)
    finally:
        os.unlink(path)


def test_no_duplicates_passes():
    """Test that items without duplicates pass."""
    items = [
        MediaItem(
            id="img_001",
            path="images/test1.jpg",
            description="Test image 1",
            media_type="image",
            format="jpg",
        ),
        MediaItem(
            id="img_002",
            path="images/test2.jpg",
            description="Test image 2",
            media_type="image",
            format="jpg",
        ),
    ]
    result = validate_no_duplicates(items)
    assert result.is_valid, "Items without duplicates should pass"


def test_media_type_match_passes():
    """Test that matching media_type and format pass."""
    items = [
        MediaItem(
            id="img_001",
            path="images/test.jpg",
            description="A test image",
            media_type="image",
            format="jpg",
        ),
        MediaItem(
            id="vid_001",
            path="videos/test.mp4",
            description="A test video",
            media_type="video",
            format="mp4",
        ),
    ]
    result = validate_media_type_matches_format(items)
    assert result.is_valid, "Matching media_type and format should pass"


def test_validate_dataset_with_missing_media_root():
    """Test that missing media root generates a warning."""
    items = [
        MediaItem(
            id="img_001",
            path="nonexistent/test.jpg",
            description="A test image",
            media_type="image",
            format="jpg",
        ),
    ]
    dataset = MediaDataset(version="1.0", items=items)

    # Save to temp file
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    dataset.save(path)

    try:
        # Validate with a non-existent media root
        result = validate_dataset(path, media_root="/nonexistent/path", skip_file_check=False)
        # Should have warnings about missing directory or files
        assert len(result.warnings) > 0, "Should have warnings for missing files"
    finally:
        os.unlink(path)
