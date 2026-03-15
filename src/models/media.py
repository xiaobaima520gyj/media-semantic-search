"""Media models using Pydantic v2."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# Supported media formats
IMAGE_FORMATS = frozenset({"jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff"})
VIDEO_FORMATS = frozenset({"mp4", "mov", "avi", "webm", "mkv", "flv"})
ALL_FORMATS = IMAGE_FORMATS | VIDEO_FORMATS


class MediaItem(BaseModel):
    """Represents a single media item in the dataset."""

    id: str = Field(..., description="Unique identifier for the media item")
    path: str = Field(..., description="Relative path to the media file")
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Text description of the media content"
    )
    media_type: Literal["image", "video"] = Field(
        ...,
        description="Type of media: image or video"
    )
    format: str = Field(..., description="File extension (e.g., jpg, mp4)")
    categories: List[str] = Field(
        default_factory=list,
        description="Hierarchical classifications for the media"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Flat tags for additional metadata"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )

    @field_validator("format", mode="before")
    @classmethod
    def normalize_format(cls, v: str) -> str:
        """Normalize format to lowercase."""
        if isinstance(v, str):
            return v.lower().lstrip(".")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate that format is supported."""
        if v not in ALL_FORMATS:
            raise ValueError(
                f"Unsupported format: {v}. "
                f"Supported formats: {', '.join(sorted(ALL_FORMATS))}"
            )
        return v

    @model_validator(mode="after")
    def validate_media_type_matches_format(self) -> "MediaItem":
        """Ensure media_type matches the format category."""
        # Determine expected media type based on format
        if self.format in IMAGE_FORMATS:
            expected_type = "image"
        elif self.format in VIDEO_FORMATS:
            expected_type = "video"
        else:
            # Format is already validated above, this is a safety check
            return self

        if self.media_type != expected_type:
            raise ValueError(
                f"media_type '{self.media_type}' does not match format '{self.format}'. "
                f"Format '{self.format}' is a {'image' if self.format in IMAGE_FORMATS else 'video'}."
            )
        return self


class MediaDataset(BaseModel):
    """Container for a collection of media items."""

    version: str = Field(
        default="1.0",
        description="Dataset version string"
    )
    items: List[MediaItem] = Field(
        default_factory=list,
        description="List of media items in the dataset"
    )

    def save(self, path: str) -> None:
        """Save dataset to a JSON file with pretty formatting."""
        file_path = Path(path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                self.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False
            )

    @classmethod
    def load(cls, path: str) -> "MediaDataset":
        """Load dataset from a JSON file."""
        file_path = Path(path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)
