"""Validation result types for dataset validation."""

import os
from pathlib import Path
from typing import List, Optional

from src.models.media import IMAGE_FORMATS, VIDEO_FORMATS, MediaDataset, MediaItem


class ValidationError:
    """Represents a single validation error."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"

    def __str__(self) -> str:
        return "[{0}] {1}: {2}".format(self.severity.upper(), self.field, self.message)

    def __repr__(self) -> str:
        return "ValidationError(field={0!r}, message={1!r}, severity={2!r})".format(
            self.field, self.message, self.severity
        )


class ValidationResult:
    """Result of dataset validation."""

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []

    def add_error(self, field: str, message: str, severity: str = "error"):
        """Add a validation error."""
        error = ValidationError(field=field, message=message, severity=severity)
        self.errors.append(error)
        if severity == "error":
            self.is_valid = False

    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)

    @property
    def summary(self) -> str:
        """Generate a summary string."""
        error_count = sum(1 for e in self.errors if e.severity == "error")
        warning_count = len(self.errors) + len(self.warnings) - error_count

        parts = []
        if error_count > 0:
            parts.append("{0} error(s)".format(error_count))
        if warning_count > 0:
            parts.append("{0} warning(s)".format(warning_count))

        if not parts:
            return "Validation passed"

        status = "FAILED" if not self.is_valid else "passed with warnings"
        return "Validation {0}: {1}".format(status, ", ".join(parts))


def validate_file_exists(
    items: List[MediaItem], dataset_path: str, media_root: Optional[str] = None
) -> ValidationResult:
    """
    Validate that all media files exist on the filesystem.

    Args:
        items: List of media items to validate
        dataset_path: Path to the dataset JSON file (used to resolve relative paths)
        media_root: Optional root directory for media files.
                    If None, uses the directory containing the dataset file.

    Returns:
        ValidationResult with errors for missing files
    """
    result = ValidationResult()

    # Determine the media root directory
    if media_root is None:
        dataset_dir = os.path.dirname(os.path.abspath(dataset_path))
        media_root = dataset_dir
    else:
        media_root = os.path.abspath(media_root)

    # Check if media root exists
    if not os.path.isdir(media_root):
        result.add_warning("Media root directory does not exist: {0}".format(media_root))
        return result

    # Check each item
    for item in items:
        media_path = os.path.join(media_root, item.path)
        if not os.path.isfile(media_path):
            result.add_error(
                field=item.id,
                message="File not found: {0}".format(item.path),
                severity="warning"
            )

    return result


def validate_media_type_matches_format(items: List[MediaItem]) -> ValidationResult:
    """
    Validate that media_type matches the format extension.

    Args:
        items: List of media items to validate

    Returns:
        ValidationResult with errors for mismatches
    """
    result = ValidationResult()

    for item in items:
        # Determine expected media type based on format
        if item.format in IMAGE_FORMATS:
            expected_type = "image"
        elif item.format in VIDEO_FORMATS:
            expected_type = "video"
        else:
            # Format validation is handled by Pydantic, skip here
            continue

        if item.media_type != expected_type:
            result.add_error(
                field=item.id,
                message="media_type '{0}' does not match format '{1}' (expected '{2}')".format(
                    item.media_type, item.format, expected_type
                ),
                severity="error"
            )

    return result


def validate_no_duplicates(items: List[MediaItem]) -> ValidationResult:
    """
    Check for duplicate IDs and paths in the dataset.

    Args:
        items: List of media items to validate

    Returns:
        ValidationResult with errors for duplicates
    """
    result = ValidationResult()

    # Check for duplicate IDs
    ids = [item.id for item in items]
    seen_ids = set()
    for item_id in ids:
        if item_id in seen_ids:
            result.add_error(
                field="duplicate_id",
                message="Duplicate ID found: {0}".format(item_id),
                severity="error"
            )
        seen_ids.add(item_id)

    # Check for duplicate paths
    paths = [item.path for item in items]
    seen_paths = set()
    for path in paths:
        if path in seen_paths:
            result.add_error(
                field="duplicate_path",
                message="Duplicate path found: {0}".format(path),
                severity="error"
            )
        seen_paths.add(path)

    return result


def validate_dataset(
    dataset_path: str,
    media_root: Optional[str] = None,
    skip_file_check: bool = False
) -> ValidationResult:
    """
    Run all validations on a dataset.

    This is the main entry point for dataset validation.

    Args:
        dataset_path: Path to the dataset JSON file
        media_root: Optional root directory for media files.
                    If None, uses the directory containing the dataset file.
        skip_file_check: If True, skips file existence validation
                         (useful for testing without actual media files)

    Returns:
        Combined ValidationResult from all validations
    """
    result = ValidationResult()

    try:
        # Load dataset (this runs Pydantic schema validation)
        dataset = MediaDataset.load(dataset_path)
    except Exception as e:
        result.add_error(
            field="schema",
            message="Failed to load dataset: {0}".format(str(e)),
            severity="error"
        )
        return result

    items = dataset.items

    # Run file existence validation (optional)
    if not skip_file_check:
        file_result = validate_file_exists(items, dataset_path, media_root)
        result.errors.extend(file_result.errors)
        result.warnings.extend(file_result.warnings)
        if not file_result.is_valid:
            result.is_valid = False

    # Run media type validation
    type_result = validate_media_type_matches_format(items)
    result.errors.extend(type_result.errors)
    result.warnings.extend(type_result.warnings)
    if not type_result.is_valid:
        result.is_valid = False

    # Run duplicate detection
    dup_result = validate_no_duplicates(items)
    result.errors.extend(dup_result.errors)
    result.warnings.extend(dup_result.warnings)
    if not dup_result.is_valid:
        result.is_valid = False

    return result
