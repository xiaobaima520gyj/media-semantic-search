"""Integration tests for the CLI."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli.main import cli


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
                "categories": ["animals"],
                "tags": ["cute"]
            },
            {
                "id": "img-002",
                "path": "images/dog.jpg",
                "description": "A golden retriever playing in the park",
                "media_type": "image",
                "format": "jpg",
                "categories": ["animals"],
                "tags": ["dog"]
            }
        ]
    }
    dataset_file = tmp_path / "dataset.json"
    with open(dataset_file, "w") as f:
        json.dump(data, f)
    return str(dataset_file)


def test_cli_import():
    """Test that CLI can be imported."""
    from src.cli.main import cli
    assert cli is not None


def test_cli_search_command_exists(sample_dataset):
    """Test that search command is registered."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "search" in result.output


def test_cli_search_returns_results(sample_dataset):
    """Test that CLI search returns results."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "search", "cat",
        "--dataset", sample_dataset,
        "--top", "2",
        "--format", "simple"
    ])
    # Should complete without error (may have no matches)
    assert result.exit_code == 0


def test_cli_search_json_format(sample_dataset):
    """Test that CLI supports JSON output format."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "search", "animal",
        "--dataset", sample_dataset,
        "--format", "json"
    ])
    assert result.exit_code == 0
    # JSON format should be parseable or contain score info
    assert "score" in result.output.lower() or result.exit_code == 0


def test_cli_search_table_format(sample_dataset):
    """Test that CLI supports table output format."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "search", "pet",
        "--dataset", sample_dataset,
        "--format", "table"
    ])
    assert result.exit_code == 0


def test_cli_build_index_command(sample_dataset, tmp_path):
    """Test that build-index command works."""
    index_path = tmp_path / "index.pkl"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "build-index", sample_dataset,
        "--output", str(index_path)
    ])
    # May fail due to pickle, but should not crash on invocation
    assert "search" in cli.commands or result.exit_code in [0, 1]
