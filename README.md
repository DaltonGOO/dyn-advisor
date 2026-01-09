# dyn-advisor

A small, inspectable agent that indexes a Dynamo graph repository, recommends graphs based on user intent, explains why, and can optionally execute a graph via Dynamo CLI with explicit consent.

## Features

- **🔍 Graph Indexing**: Parses `.dyn` files and documentation to build a searchable catalog
- **🎯 Intent-Based Recommendations**: Ranks and recommends graphs based on user queries
- **💡 Explanations**: Provides clear explanations for why each graph is recommended
- **✅ Safe Execution**: Optional execution via Dynamo CLI with multiple safety layers
- **📝 Full Traceability**: All actions are logged and auditable
- **🔒 Security First**: No secrets in code, execution off by default

## Installation

```bash
# Clone the repository
git clone https://github.com/DaltonGOO/dyn-advisor.git
cd dyn-advisor

# Install dependencies
pip install -e .
```

## Configuration

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` to configure your setup:
   ```bash
   # Required: Path to your Dynamo graphs
   GRAPH_REPO_PATH=./examples/graphs

   # Optional: Path to documentation
   DOCS_PATH=./examples/docs

   # Execution control (default: false for safety)
   ALLOW_EXECUTION=false

   # Required for execution: Path to Dynamo CLI
   DYNAMO_CLI_PATH=/path/to/DynamoSandbox.exe
   ```

## Usage

### Check Status

```bash
dyn-advisor status
```

Shows current configuration and safety status.

### Index Graphs

```bash
dyn-advisor index
```

Builds the catalog by indexing all `.dyn` files in your graph repository.

### Get Recommendations

```bash
dyn-advisor recommend "create rectangle"
```

Recommends graphs based on your query with explanations.

Options:
- `--max-results N`: Limit number of recommendations (default: 5)
- `--explain`: Show detailed explanations for each recommendation
- `--run`: Execute the top recommended graph (requires safety flags)

### Execute a Graph

```bash
# Preview graph information
dyn-advisor execute "Simple Rectangle Creator"

# Execute with explicit consent
dyn-advisor execute "Simple Rectangle Creator" --run
```

**Important**: Execution requires:
1. `ALLOW_EXECUTION=true` in `.env`
2. Valid `DYNAMO_CLI_PATH` in `.env`
3. `--run` flag on the command line

All three conditions must be met for execution to proceed.

## Safety & Security

### Execution is Off by Default

Execution is disabled by default and requires **explicit consent at three levels**:

1. **Configuration**: `ALLOW_EXECUTION=true` must be set in `.env`
2. **CLI Path**: `DYNAMO_CLI_PATH` must point to a valid executable
3. **Runtime Flag**: `--run` must be provided on the command line

### No Secrets in Code

All configuration is done via `.env` file, which is gitignored. Never commit:
- Dynamo CLI paths
- API keys or credentials
- Environment-specific settings

### Full Traceability

All actions are logged:
- Recommendation requests and results
- Execution attempts (allowed or blocked)
- Configuration checks
- Errors and warnings

Logs are written to both console and file (configurable via `LOG_FILE`).

## Examples

The `examples/` directory contains sample graphs and documentation:

```
examples/
├── graphs/          # Sample .dyn files
│   ├── simple_rectangle.dyn
│   ├── wall_analyzer.dyn
│   └── point_grid.dyn
└── docs/            # Documentation
    └── graph_documentation.md
```

Try the examples:

```bash
# Index the example graphs
dyn-advisor index --graph-repo ./examples/graphs --docs-path ./examples/docs

# Get recommendations
dyn-advisor recommend "geometry" --explain
dyn-advisor recommend "wall analysis"
dyn-advisor recommend "simple shape"
```

## How It Works

1. **Parsing**: The parser reads `.dyn` files (JSON format) and extracts:
   - Graph name, description, and category
   - Node types and counts
   - Connector information
   - Metadata (author, UUID, etc.)

2. **Cataloging**: All parsed graphs are indexed into a searchable catalog

3. **Ranking**: User queries are matched against:
   - Graph names
   - Descriptions
   - Categories
   - Node types
   - Documentation content

4. **Explanation**: Each recommendation includes reasons like:
   - "Name matches 'Simple Rectangle Creator'"
   - "Category 'Geometry' matches"
   - "Contains 3 relevant node(s)"
   - "Simple graph with 3 nodes"

5. **Execution** (optional): With explicit consent, graphs can be executed via Dynamo CLI

## Architecture

```
dyn_advisor/
├── __init__.py       # Package initialization
├── cli.py            # Command-line interface
├── parser.py         # .dyn file parser
├── catalog.py        # Graph catalog manager
├── recommender.py    # Recommendation engine
└── executor.py       # Dynamo execution interface
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check .

# Run formatter
ruff format .
```

## License

See [LICENSE](LICENSE) file for details.

## Contributing

This project demonstrates how an agent can sit inside an existing Dynamo workflow, providing discovery, guidance, and optional execution with full traceability. Contributions are welcome!
