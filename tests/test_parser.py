"""
Tests for the parser module.
"""

import json
import tempfile
from pathlib import Path

from dyn_advisor.parser import DynParser


def test_parse_valid_dyn_file():
    """Test parsing a valid .dyn file."""
    parser = DynParser()

    # Create a temporary .dyn file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dyn', delete=False) as f:
        data = {
            'Name': 'Test Graph',
            'Description': 'A test graph',
            'Category': 'Testing',
            'Author': 'Test User',
            'Uuid': 'test-uuid-123',
            'Nodes': [
                {'Id': 'node1', 'Name': 'Node1', 'ConcreteType': 'Type1'},
                {'Id': 'node2', 'Name': 'Node2', 'ConcreteType': 'Type2'},
            ],
            'Connectors': [
                {'Start': 'node1', 'End': 'node2'},
            ],
            'View': {'X': 0, 'Y': 0, 'Zoom': 1.0}
        }
        json.dump(data, f)
        temp_path = Path(f.name)

    try:
        metadata = parser.parse_dyn_file(temp_path)

        assert metadata is not None
        assert metadata['name'] == 'Test Graph'
        assert metadata['description'] == 'A test graph'
        assert metadata['category'] == 'Testing'
        assert metadata['author'] == 'Test User'
        assert metadata['uuid'] == 'test-uuid-123'
        assert metadata['node_count'] == 2
        assert metadata['connector_count'] == 1
        assert len(metadata['nodes']) == 2
    finally:
        temp_path.unlink()


def test_parse_invalid_json():
    """Test parsing an invalid JSON file."""
    parser = DynParser()

    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dyn', delete=False) as f:
        f.write('{ invalid json')
        temp_path = Path(f.name)

    try:
        metadata = parser.parse_dyn_file(temp_path)
        assert metadata is None
    finally:
        temp_path.unlink()


def test_parse_nonexistent_file():
    """Test parsing a file that doesn't exist."""
    parser = DynParser()

    metadata = parser.parse_dyn_file(Path('/nonexistent/file.dyn'))
    assert metadata is None


def test_parse_documentation():
    """Test parsing documentation files."""
    parser = DynParser()

    # Create a temporary documentation file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('# Test Documentation\n\nThis is a test.')
        temp_path = Path(f.name)

    try:
        doc_metadata = parser.parse_documentation(temp_path)

        assert doc_metadata is not None
        assert 'content' in doc_metadata
        assert 'Test Documentation' in doc_metadata['content']
        assert doc_metadata['filename'] == temp_path.name
    finally:
        temp_path.unlink()
