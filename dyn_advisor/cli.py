"""
CLI interface for dyn-advisor.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from .catalog import GraphCatalog
from .executor import DynamoExecutor
from .recommender import RecommendationEngine


# Configure logging
def setup_logging(log_level: str, log_file: Optional[str] = None):
    """Setup logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    return logging.getLogger('dyn-advisor')


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """dyn-advisor: Dynamo graph recommendation and execution agent.

    A small, inspectable agent that indexes a Dynamo graph repository,
    recommends graphs based on user intent, explains why, and can
    optionally execute a graph via Dynamo CLI with explicit consent.
    """
    pass


@cli.command()
@click.option('--graph-repo', default=None, help='Path to graph repository (overrides .env)')
@click.option('--docs-path', default=None, help='Path to documentation (overrides .env)')
def index(graph_repo: Optional[str], docs_path: Optional[str]):
    """Build the catalog by indexing all .dyn files."""
    # Load environment
    load_dotenv()

    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE')
    logger = setup_logging(log_level, log_file)

    # Get paths
    repo_path = graph_repo or os.getenv('GRAPH_REPO_PATH', './graphs')
    doc_path = docs_path or os.getenv('DOCS_PATH', './docs')

    logger.info("=" * 80)
    logger.info("INDEXING GRAPHS")
    logger.info("=" * 80)
    logger.info(f"Graph repository: {repo_path}")
    logger.info(f"Documentation path: {doc_path}")

    # Build catalog
    catalog = GraphCatalog(repo_path, doc_path)
    catalog.set_logger(logger)

    count = catalog.build_catalog()

    logger.info("=" * 80)
    logger.info(f"INDEXING COMPLETE: {count} graphs indexed")
    logger.info("=" * 80)

    # Display summary
    click.echo(f"\n✓ Indexed {count} Dynamo graphs from {repo_path}")

    if count > 0:
        click.echo("\nSample graphs:")
        for i, graph in enumerate(catalog.get_all_graphs()[:5], 1):
            click.echo(f"  {i}. {graph['name']} ({graph['node_count']} nodes)")


@cli.command()
@click.argument('query')
@click.option('--max-results', default=5, help='Maximum number of recommendations')
@click.option('--graph-repo', default=None, help='Path to graph repository (overrides .env)')
@click.option('--docs-path', default=None, help='Path to documentation (overrides .env)')
@click.option(
    '--run', is_flag=True, default=False,
    help='Execute the top recommended graph (requires ALLOW_EXECUTION=true)'
)
@click.option(
    '--explain', is_flag=True, default=False,
    help='Show detailed explanation for each recommendation'
)
def recommend(query: str, max_results: int, graph_repo: Optional[str],
              docs_path: Optional[str], run: bool, explain: bool):
    """Recommend graphs based on user query/intent."""
    # Load environment
    load_dotenv()

    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE')
    logger = setup_logging(log_level, log_file)

    # Get paths
    repo_path = graph_repo or os.getenv('GRAPH_REPO_PATH', './graphs')
    doc_path = docs_path or os.getenv('DOCS_PATH', './docs')

    logger.info("=" * 80)
    logger.info("RECOMMENDATION REQUEST")
    logger.info("=" * 80)
    logger.info(f"Query: {query}")
    logger.info(f"Max results: {max_results}")
    logger.info(f"Run flag: {run}")

    # Build catalog
    catalog = GraphCatalog(repo_path, doc_path)
    catalog.set_logger(logger)
    catalog.build_catalog()

    if len(catalog.get_all_graphs()) == 0:
        click.echo(f"\n⚠ No graphs found in {repo_path}")
        click.echo("Run 'dyn-advisor index' first or check your GRAPH_REPO_PATH")
        return

    # Get recommendations
    engine = RecommendationEngine(catalog)
    engine.set_logger(logger)

    recommendations = engine.recommend(query, max_results)

    if not recommendations:
        logger.info("No recommendations found")
        click.echo(f"\n⚠ No graphs match your query: '{query}'")
        return

    logger.info(f"Found {len(recommendations)} recommendations")
    logger.info("=" * 80)

    # Display recommendations
    click.echo(f"\n📋 Recommendations for: '{query}'")
    click.echo("=" * 80)

    for i, (graph, score, explanation) in enumerate(recommendations, 1):
        click.echo(f"\n{i}. {graph['name']} (score: {score:.1f})")
        click.echo(f"   {explanation}")
        click.echo(f"   Category: {graph['category']}")
        click.echo(f"   Nodes: {graph['node_count']}, Connectors: {graph['connector_count']}")
        click.echo(f"   Path: {graph['filepath']}")

        if explain:
            click.echo("\n   Detailed explanation:")
            detailed = engine.explain_recommendation(graph, query)
            for line in detailed.split('\n'):
                if line.strip():
                    click.echo(f"   {line}")

    # Handle execution if --run flag is provided
    if run:
        if not recommendations:
            click.echo("\n⚠ No graph to execute")
            return

        top_graph = recommendations[0][0]

        click.echo("\n" + "=" * 80)
        click.echo("EXECUTION REQUEST")
        click.echo("=" * 80)

        # Check execution configuration
        allow_execution = os.getenv('ALLOW_EXECUTION', 'false').lower() == 'true'
        dynamo_cli_path = os.getenv('DYNAMO_CLI_PATH', '')

        executor = DynamoExecutor(dynamo_cli_path, allow_execution)
        executor.set_logger(logger)

        # Execute
        result = executor.execute_graph(top_graph, run_flag=True)

        if result['executed']:
            if result['success']:
                click.echo(f"\n✓ {result['message']}")
                if result['output']:
                    click.echo(f"\nOutput:\n{result['output']}")
            else:
                click.echo(f"\n✗ {result['message']}")
                if result['error']:
                    click.echo(f"\nError:\n{result['error']}")
        else:
            click.echo(f"\n⚠ {result['message']}")

        logger.info("=" * 80)


@cli.command()
@click.argument('graph_name')
@click.option('--graph-repo', default=None, help='Path to graph repository (overrides .env)')
@click.option(
    '--run', is_flag=True, default=False,
    help='Execute the graph (requires ALLOW_EXECUTION=true)'
)
def execute(graph_name: str, graph_repo: Optional[str], run: bool):
    """Execute a specific graph by name."""
    # Load environment
    load_dotenv()

    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE')
    logger = setup_logging(log_level, log_file)

    # Get paths
    repo_path = graph_repo or os.getenv('GRAPH_REPO_PATH', './graphs')

    logger.info("=" * 80)
    logger.info("EXECUTION REQUEST")
    logger.info("=" * 80)
    logger.info(f"Graph name: {graph_name}")
    logger.info(f"Run flag: {run}")

    # Build catalog
    catalog = GraphCatalog(repo_path)
    catalog.set_logger(logger)
    catalog.build_catalog()

    # Find graph
    graph = catalog.get_graph_by_name(graph_name)

    if not graph:
        logger.warning(f"Graph not found: {graph_name}")
        click.echo(f"\n⚠ Graph '{graph_name}' not found")
        available = ', '.join([g['name'] for g in catalog.get_all_graphs()[:10]])
        click.echo(f"Available graphs: {available}")
        return

    logger.info(f"Found graph: {graph['name']}")

    # Display graph info
    click.echo(f"\nGraph: {graph['name']}")
    click.echo(f"Description: {graph['description'] or 'N/A'}")
    click.echo(f"Category: {graph['category']}")
    click.echo(f"Path: {graph['filepath']}")

    # Execute if --run flag is provided
    if run:
        click.echo("\n" + "=" * 80)
        click.echo("EXECUTING")
        click.echo("=" * 80)

        allow_execution = os.getenv('ALLOW_EXECUTION', 'false').lower() == 'true'
        dynamo_cli_path = os.getenv('DYNAMO_CLI_PATH', '')

        executor = DynamoExecutor(dynamo_cli_path, allow_execution)
        executor.set_logger(logger)

        result = executor.execute_graph(graph, run_flag=True)

        if result['executed']:
            if result['success']:
                click.echo(f"\n✓ {result['message']}")
                if result['output']:
                    click.echo(f"\nOutput:\n{result['output']}")
            else:
                click.echo(f"\n✗ {result['message']}")
                if result['error']:
                    click.echo(f"\nError:\n{result['error']}")
        else:
            click.echo(f"\n⚠ {result['message']}")
    else:
        click.echo("\n⚠ Add --run flag to execute this graph")

    logger.info("=" * 80)


@cli.command()
def status():
    """Show configuration and status."""
    load_dotenv()

    click.echo("\ndyn-advisor Status")
    click.echo("=" * 80)

    # Configuration
    graph_repo = os.getenv('GRAPH_REPO_PATH', './graphs')
    docs_path = os.getenv('DOCS_PATH', './docs')
    allow_execution = os.getenv('ALLOW_EXECUTION', 'false').lower() == 'true'
    dynamo_cli = os.getenv('DYNAMO_CLI_PATH', '')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'dyn-advisor.log')

    click.echo("\nConfiguration:")
    click.echo(f"  Graph repository: {graph_repo}")
    click.echo(f"  Documentation path: {docs_path}")
    click.echo(f"  Execution allowed: {allow_execution}")
    click.echo(f"  Dynamo CLI path: {dynamo_cli or '(not set)'}")
    click.echo(f"  Log level: {log_level}")
    click.echo(f"  Log file: {log_file}")

    # Check paths
    click.echo("\nPath checks:")
    repo_exists = Path(graph_repo).exists()
    click.echo(f"  Graph repository exists: {repo_exists}")
    docs_exists = Path(docs_path).exists()
    click.echo(f"  Documentation path exists: {docs_exists}")
    cli_exists = Path(dynamo_cli).exists() if dynamo_cli else False
    click.echo(f"  Dynamo CLI exists: {cli_exists}")

    # Safety status
    click.echo("\nSafety status:")
    if allow_execution:
        click.echo("  ⚠ Execution is ENABLED")
        if not dynamo_cli or not cli_exists:
            click.echo("  ⚠ But Dynamo CLI is not configured or not found")
    else:
        click.echo("  ✓ Execution is DISABLED (safe)")

    click.echo("\nTo enable execution:")
    click.echo("  1. Set ALLOW_EXECUTION=true in .env")
    click.echo("  2. Set DYNAMO_CLI_PATH to your Dynamo executable in .env")
    click.echo("  3. Use --run flag when running recommend or execute commands")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
