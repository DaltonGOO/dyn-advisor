"""
Tests for the recommender module.
"""

import json
import tempfile
from pathlib import Path

from dyn_advisor.catalog import GraphCatalog
from dyn_advisor.recommender import RecommendationEngine


def test_recommend():
    """Test recommendation based on query."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test graphs
        graphs_data = [
            {
                'Name': 'Simple Rectangle',
                'Description': 'Creates a simple rectangle',
                'Category': 'Geometry',
                'Nodes': [
                    {'Id': f'n{i}', 'Name': f'Rectangle{i}', 'ConcreteType': 'Type'}
                    for i in range(3)
                ]
            },
            {
                'Name': 'Complex Wall Analysis',
                'Description': 'Analyzes wall properties in detail',
                'Category': 'Analysis',
                'Nodes': [
                    {'Id': f'n{i}', 'Name': 'Node', 'ConcreteType': 'Type'}
                    for i in range(10)
                ]
            },
        ]

        for i, data in enumerate(graphs_data):
            dyn_file = temp_path / f'test{i}.dyn'
            full_data = {**data, 'Connectors': []}
            with open(dyn_file, 'w') as f:
                json.dump(full_data, f)

        catalog = GraphCatalog(str(temp_path))
        catalog.build_catalog()

        engine = RecommendationEngine(catalog)

        # Test simple query
        results = engine.recommend('simple', max_results=5)
        assert len(results) > 0
        # Should prefer "Simple Rectangle" due to name and simplicity bonus
        assert results[0][0]['name'] == 'Simple Rectangle'

        # Test complex query
        results = engine.recommend('complex analysis', max_results=5)
        assert len(results) > 0
        # Should prefer "Complex Wall Analysis"
        assert any(r[0]['name'] == 'Complex Wall Analysis' for r in results)


def test_explain_recommendation():
    """Test explanation generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a test graph
        dyn_file = temp_path / 'test.dyn'
        data = {
            'Name': 'Test Graph',
            'Description': 'A test description',
            'Category': 'Testing',
            'Nodes': [],
            'Connectors': []
        }
        with open(dyn_file, 'w') as f:
            json.dump(data, f)

        catalog = GraphCatalog(str(temp_path))
        catalog.build_catalog()

        engine = RecommendationEngine(catalog)
        graph = catalog.get_all_graphs()[0]

        explanation = engine.explain_recommendation(graph, 'test')

        assert 'Graph: Test Graph' in explanation
        assert 'Score:' in explanation
        assert 'Explanation:' in explanation
        assert 'Category:' in explanation


def test_empty_catalog():
    """Test recommendation with empty catalog."""
    with tempfile.TemporaryDirectory() as temp_dir:
        catalog = GraphCatalog(str(temp_dir))
        catalog.build_catalog()

        engine = RecommendationEngine(catalog)
        results = engine.recommend('anything')

        assert len(results) == 0
