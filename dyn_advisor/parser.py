"""
Parser module for extracting metadata from Dynamo (.dyn) files.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class DynParser:
    """Parses .dyn files to extract metadata and structure information."""

    def __init__(self):
        self.logger = None

    def set_logger(self, logger):
        """Set logger for this parser."""
        self.logger = logger

    def parse_dyn_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a .dyn file and extract metadata.

        Args:
            filepath: Path to the .dyn file

        Returns:
            Dictionary containing parsed metadata or None if parsing fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)

            metadata = {
                'filepath': str(filepath),
                'filename': filepath.name,
                'name': content.get('Name', filepath.stem),
                'description': content.get('Description', ''),
                'uuid': content.get('Uuid', ''),
                'author': content.get('Author', ''),
                'category': content.get('Category', 'Uncategorized'),
                'nodes': [],
                'node_count': 0,
                'connector_count': 0,
            }

            # Extract nodes information
            if 'Nodes' in content and isinstance(content['Nodes'], list):
                metadata['node_count'] = len(content['Nodes'])
                for node in content['Nodes']:
                    if isinstance(node, dict):
                        node_info = {
                            'name': node.get('Name', ''),
                            'type': node.get('ConcreteType', ''),
                            'id': node.get('Id', ''),
                        }
                        metadata['nodes'].append(node_info)

            # Extract connectors information
            if 'Connectors' in content and isinstance(content['Connectors'], list):
                metadata['connector_count'] = len(content['Connectors'])

            # Extract view information
            if 'View' in content:
                view = content['View']
                metadata['view'] = {
                    'x': view.get('X', 0),
                    'y': view.get('Y', 0),
                    'zoom': view.get('Zoom', 1.0),
                }

            if self.logger:
                self.logger.debug(f"Parsed {filepath.name}: {metadata['node_count']} nodes")

            return metadata

        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.warning(f"Failed to parse {filepath}: Invalid JSON - {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to parse {filepath}: {e}")
            return None

    def parse_documentation(self, doc_path: Path) -> Dict[str, Any]:
        """
        Parse documentation files for additional context.

        Args:
            doc_path: Path to documentation file

        Returns:
            Dictionary containing documentation metadata
        """
        try:
            if not doc_path.exists():
                return {}

            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'filepath': str(doc_path),
                'filename': doc_path.name,
                'content': content,
                'size': len(content),
            }
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to parse documentation {doc_path}: {e}")
            return {}
