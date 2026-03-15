"""Search result models for semantic search responses."""

from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Single search result with relevance score.

    Represents one item returned from a semantic search query,
    including the media item details and a similarity score.
    """

    id: str = Field(..., description="Unique identifier for the media item")
    path: str = Field(..., description="Relative path to the media file")
    description: str = Field(..., description="Text description of the media content")
    media_type: str = Field(..., description="Type of media: image or video")
    format: str = Field(..., description="File extension (e.g., jpg, mp4)")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score from 0-1, higher = more similar"
    )


class SearchResponse(BaseModel):
    """Response from semantic search API.

    Contains the original query, list of ranked results,
    and total number of matches.
    """

    query: str = Field(..., description="The original search query text")
    results: List[SearchResult] = Field(
        default_factory=list,
        description="List of search results ranked by relevance"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of matching results"
    )
