"""
Tests for the catalog module.
"""

import json
import tempfile
from pathlib import Path

from dyn_advisor.catalog import GraphCatalog


def test_build_catalog():
    """Test building a catalog from .dyn files."""
    # Create a temporary directory with .dyn files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test .dyn files
        for i in range(3):
            dyn_file = temp_path / f'test{i}.dyn'
            data = {
                'Name': f'Test Graph {i}',
                'Description': f'Description {i}',
                'Category': 'Testing',
                'Nodes': [
                    {
                        'Id': f'graph{i}_node{j}',
                        'Name': f'Node{j}',
                        'ConcreteType': 'Type',
                    }
                    for j in range(i + 1)
                ],
                'Connectors': []
            }
            with open(dyn_file, 'w') as f:
                json.dump(data, f)

        # Build catalog
        catalog = GraphCatalog(str(temp_path))
        count = catalog.build_catalog()

        assert count == 3
        assert len(catalog.get_all_graphs()) == 3


def test_get_graph_by_name():
    """Test retrieving a graph by name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a test .dyn file
        dyn_file = temp_path / 'test.dyn'
        data = {
            'Name': 'Unique Graph Name',
            'Description': 'Test',
            'Nodes': [],
            'Connectors': []
        }
        with open(dyn_file, 'w') as f:
            json.dump(data, f)

        catalog = GraphCatalog(str(temp_path))
        catalog.build_catalog()

        # Test exact match
        graph = catalog.get_graph_by_name('Unique Graph Name')
        assert graph is not None
        assert graph['name'] == 'Unique Graph Name'

        # Test case-insensitive match
        graph = catalog.get_graph_by_name('unique graph name')
        assert graph is not None

        # Test non-existent graph
        graph = catalog.get_graph_by_name('Nonexistent')
        assert graph is None


def test_search_graphs():
    """Test searching for graphs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test .dyn files with different attributes
        graphs_data = [
            {
                'Name': 'Rectangle Creator',
                'Description': 'Creates rectangles',
                'Category': 'Geometry',
            },
            {
                'Name': 'Circle Generator',
                'Description': 'Generates circles',
                'Category': 'Geometry',
            },
            {'Name': 'Wall Analyzer', 'Description': 'Analyzes walls', 'Category': 'Analysis'},
        ]

        for i, data in enumerate(graphs_data):
            dyn_file = temp_path / f'test{i}.dyn'
            full_data = {**data, 'Nodes': [], 'Connectors': []}
            with open(dyn_file, 'w') as f:
                json.dump(full_data, f)

        catalog = GraphCatalog(str(temp_path))
        catalog.build_catalog()

        # Search by category
        results = catalog.search_graphs('Geometry')
        assert len(results) == 2

        # Search by name
        results = catalog.search_graphs('Rectangle')
        assert len(results) == 1
        assert results[0]['name'] == 'Rectangle Creator'

        # Search by description
        results = catalog.search_graphs('Analyzes')
        assert len(results) == 1
