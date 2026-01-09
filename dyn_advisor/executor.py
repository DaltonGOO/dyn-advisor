"""
Execution module for running Dynamo graphs via CLI with explicit consent.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class DynamoExecutor:
    """Handles execution of Dynamo graphs with safety controls."""
    
    def __init__(self, dynamo_cli_path: str, allow_execution: bool = False):
        """
        Initialize the Dynamo executor.
        
        Args:
            dynamo_cli_path: Path to Dynamo CLI executable
            allow_execution: Whether execution is allowed (from config)
        """
        self.dynamo_cli_path = dynamo_cli_path
        self.allow_execution = allow_execution
        self.logger = None
    
    def set_logger(self, logger):
        """Set logger for this executor."""
        self.logger = logger
    
    def can_execute(self) -> bool:
        """
        Check if execution is allowed and configured.
        
        Returns:
            True if execution is possible, False otherwise
        """
        if not self.allow_execution:
            return False
        
        if not self.dynamo_cli_path:
            return False
        
        cli_path = Path(self.dynamo_cli_path)
        if not cli_path.exists():
            if self.logger:
                self.logger.warning(f"Dynamo CLI not found at: {self.dynamo_cli_path}")
            return False
        
        return True
    
    def execute_graph(self, graph: Dict[str, Any], run_flag: bool = False) -> Dict[str, Any]:
        """
        Execute a Dynamo graph with safety checks.
        
        Args:
            graph: Graph metadata including filepath
            run_flag: Whether the --run flag was provided (explicit consent)
            
        Returns:
            Dictionary containing execution results
        """
        result = {
            'success': False,
            'executed': False,
            'message': '',
            'output': '',
            'error': '',
        }
        
        # Safety check: Execution must be allowed in config
        if not self.allow_execution:
            result['message'] = (
                "Execution is disabled. Set ALLOW_EXECUTION=true in .env to enable."
            )
            if self.logger:
                self.logger.warning("Execution attempt blocked: ALLOW_EXECUTION=false")
            return result
        
        # Safety check: --run flag must be provided (explicit consent)
        if not run_flag:
            result['message'] = (
                "Execution requires explicit consent. Use --run flag to execute."
            )
            if self.logger:
                self.logger.info("Execution skipped: --run flag not provided")
            return result
        
        # Check if execution is possible
        if not self.can_execute():
            result['message'] = (
                "Execution not configured. Check DYNAMO_CLI_PATH in .env"
            )
            if self.logger:
                self.logger.error("Execution failed: CLI not configured")
            return result
        
        # Get graph file path
        graph_path = Path(graph['filepath'])
        if not graph_path.exists():
            result['message'] = f"Graph file not found: {graph_path}"
            if self.logger:
                self.logger.error(f"Execution failed: {result['message']}")
            return result
        
        # Log execution attempt
        if self.logger:
            self.logger.info(f"EXECUTING GRAPH: {graph['name']}")
            self.logger.info(f"  Path: {graph_path}")
            self.logger.info(f"  CLI: {self.dynamo_cli_path}")
        
        try:
            # Execute the graph using Dynamo CLI
            # Note: Actual command may vary based on Dynamo version
            cmd = [self.dynamo_cli_path, str(graph_path)]
            
            if self.logger:
                self.logger.debug(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            result['executed'] = True
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
            if result['success']:
                result['message'] = f"Graph '{graph['name']}' executed successfully"
                if self.logger:
                    self.logger.info(f"EXECUTION SUCCESSFUL: {graph['name']}")
            else:
                result['message'] = f"Graph '{graph['name']}' execution failed with code {process.returncode}"
                if self.logger:
                    self.logger.error(f"EXECUTION FAILED: {graph['name']} (code {process.returncode})")
            
            # Log output
            if self.logger and result['output']:
                self.logger.debug(f"Output: {result['output']}")
            if self.logger and result['error']:
                self.logger.debug(f"Error: {result['error']}")
            
        except subprocess.TimeoutExpired:
            result['message'] = f"Graph '{graph['name']}' execution timed out"
            if self.logger:
                self.logger.error(f"EXECUTION TIMEOUT: {graph['name']}")
        except Exception as e:
            result['message'] = f"Graph '{graph['name']}' execution error: {e}"
            if self.logger:
                self.logger.error(f"EXECUTION ERROR: {graph['name']} - {e}")
        
        return result
