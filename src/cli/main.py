"""Media Search CLI - Command-line interface for semantic media search."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from src.api import MediaSearch

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Media Dataset Search - Find images and videos by description.

    A semantic search tool that lets you find media files using
    natural language queries.
    """
    pass


@cli.command()
@click.argument("query")
@click.option("-n", "--top", default=5, help="Number of results to return")
@click.option(
    "-f", "--format",
    type=click.Choice(["table", "json", "simple"]),
    default="table",
    help="Output format"
)
@click.option(
    "-d", "--dataset",
    default="data/dataset.json",
    help="Path to the dataset JSON file"
)
@click.option(
    "-i", "--index",
    default=None,
    help="Path to pre-built index (optional, for faster loading)"
)
def search(query: str, top: int, format: str, dataset: str, index: str | None):
    """Search for media items matching QUERY.

    Examples:

        media-search search "cats on windowsill"

        media-search search "sunset" --top 10 --format json

        media-search search "beach video" --dataset my_dataset.json
    """
    try:
        # Initialize search with dataset
        search_api = MediaSearch(dataset, index_path=index)

        # Perform search
        results = search_api.query(query, top_k=top)

        # Format output based on choice
        if format == "json":
            _output_json(results)
        elif format == "simple":
            _output_simple(results)
        else:  # table
            _output_table(results, query)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise click.Abort()


def _output_json(results):
    """Output results as JSON."""
    data = [r.model_dump() for r in results]
    console.print_json(data=json.dumps(data, indent=2))


def _output_simple(results):
    """Output results in simple format (score + path)."""
    for r in results:
        console.print(f"{r.score:.4f}  {r.path}")


def _output_table(results, query: str):
    """Output results as a formatted table."""
    table = Table(title=f"Search: '{query}'")
    table.add_column("Score", style="cyan", justify="right")
    table.add_column("Path", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Description", style="white")

    for r in results:
        # Truncate description for table display
        desc = r.description[:60] + "..." if len(r.description) > 60 else r.description
        table.add_row(
            f"{r.score:.4f}",
            r.path,
            f"{r.media_type}/{r.format}",
            desc
        )

    console.print(table)


@cli.command()
@click.argument("dataset")
@click.option(
    "-o", "--output",
    default="data/index.pkl",
    help="Path to save the index"
)
def build_index(dataset: str, output: str):
    """Build and save a search index from DATASET.

    This command pre-builds the search index so that subsequent
    searches load faster.

    Example:

        media-search build-index data/dataset.json -o data/index.pkl
    """
    from src.models.media import MediaDataset
    from src.search import SemanticSearch

    try:
        console.print(f"Loading dataset: {dataset}")
        media_dataset = MediaDataset.load(dataset)
        console.print(f"Loaded {len(media_dataset.items)} items")

        console.print("Building search index...")
        search = SemanticSearch()
        search.build_index(media_dataset)

        console.print(f"Saving index to: {output}")
        search.save_index(output)

        console.print("[green]Index built successfully![/green]")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error building index:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
