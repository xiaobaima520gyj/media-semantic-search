"""High-level MediaSearch API for simple one-line search."""

from pathlib import Path
from typing import List, Optional

from src.models.media import MediaDataset
from src.search import SemanticSearch, SearchResult


class MediaSearch:
    """High-level media search API.

    Combines dataset loading, index building, and searching
    into a single simple interface.

    Example:
        from src.api import MediaSearch
        search = MediaSearch("data/dataset.json")
        results = search.query("cats on windowsill", top_k=10)
        for r in results:
            print(f"{r.path} (score: {r.score})")
    """

    def __init__(self, dataset_path: str, index_path: Optional[str] = None):
        """Initialize MediaSearch with dataset.

        Args:
            dataset_path: Path to the JSON dataset file.
            index_path: Optional path to pre-built index for faster loading.
        """
        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        self.dataset = MediaDataset.load(str(self.dataset_path))

        if index_path and Path(index_path).exists():
            self.search = SemanticSearch.load_index(index_path)
        else:
            self.search = SemanticSearch()
            self.search.build_index(self.dataset)

    def query(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for media items matching the query.

        Args:
            query: The search query text.
            top_k: Maximum number of results to return. Defaults to 5.

        Returns:
            List of SearchResult objects sorted by relevance score.
        """
        response = self.search.search(query, top_k=top_k)
        return response.results
