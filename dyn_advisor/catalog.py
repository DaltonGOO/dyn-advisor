"""
Catalog module for indexing and managing Dynamo graphs.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .parser import DynParser


class GraphCatalog:
    """Manages the catalog of indexed Dynamo graphs."""
    
    def __init__(self, graph_repo_path: str, docs_path: Optional[str] = None):
        """
        Initialize the graph catalog.
        
        Args:
            graph_repo_path: Path to the repository of .dyn files
            docs_path: Optional path to documentation files
        """
        self.graph_repo_path = Path(graph_repo_path)
        self.docs_path = Path(docs_path) if docs_path else None
        self.parser = DynParser()
        self.graphs: List[Dict[str, Any]] = []
        self.docs: List[Dict[str, Any]] = []
        self.logger = None
    
    def set_logger(self, logger):
        """Set logger for this catalog."""
        self.logger = logger
        self.parser.set_logger(logger)
    
    def build_catalog(self) -> int:
        """
        Build the catalog by indexing all .dyn files in the repository.
        
        Returns:
            Number of graphs indexed
        """
        self.graphs = []
        
        if not self.graph_repo_path.exists():
            if self.logger:
                self.logger.warning(f"Graph repository path does not exist: {self.graph_repo_path}")
            return 0
        
        # Find all .dyn files
        dyn_files = list(self.graph_repo_path.rglob('*.dyn'))
        
        if self.logger:
            self.logger.info(f"Found {len(dyn_files)} .dyn files to index")
        
        # Parse each .dyn file
        for dyn_file in dyn_files:
            metadata = self.parser.parse_dyn_file(dyn_file)
            if metadata:
                self.graphs.append(metadata)
        
        # Index documentation if available
        if self.docs_path and self.docs_path.exists():
            doc_files = list(self.docs_path.rglob('*.md')) + list(self.docs_path.rglob('*.txt'))
            if self.logger:
                self.logger.info(f"Found {len(doc_files)} documentation files")
            
            for doc_file in doc_files:
                doc_metadata = self.parser.parse_documentation(doc_file)
                if doc_metadata:
                    self.docs.append(doc_metadata)
        
        if self.logger:
            self.logger.info(f"Catalog built: {len(self.graphs)} graphs indexed")
        
        return len(self.graphs)
    
    def get_all_graphs(self) -> List[Dict[str, Any]]:
        """Get all indexed graphs."""
        return self.graphs
    
    def get_graph_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a graph by its name.
        
        Args:
            name: Name of the graph
            
        Returns:
            Graph metadata or None if not found
        """
        for graph in self.graphs:
            if graph['name'].lower() == name.lower():
                return graph
        return None
    
    def search_graphs(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for graphs matching a query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching graphs
        """
        query_lower = query.lower()
        results = []
        
        for graph in self.graphs:
            # Search in name, description, category, and node names
            searchable_text = (
                f"{graph['name']} {graph['description']} {graph['category']} "
                f"{' '.join([node['name'] for node in graph['nodes']])}"
            ).lower()
            
            if query_lower in searchable_text:
                results.append(graph)
        
        return results
