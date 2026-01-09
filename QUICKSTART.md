# Quick Start Guide

This guide will help you get started with dyn-advisor in just a few minutes.

## Installation

```bash
# Clone and install
git clone https://github.com/DaltonGOO/dyn-advisor.git
cd dyn-advisor
pip install -e .
```

## Quick Demo with Examples

### 1. Check Status

```bash
dyn-advisor status
```

This shows your current configuration and whether execution is enabled.

### 2. Index the Example Graphs

```bash
dyn-advisor index --graph-repo ./examples/graphs --docs-path ./examples/docs
```

This will index the 3 example graphs included in the repository.

### 3. Get Recommendations

Try these example queries:

```bash
# Find geometry-related graphs
dyn-advisor recommend "geometry" --graph-repo ./examples/graphs

# Find wall analysis graphs with detailed explanations
dyn-advisor recommend "wall analysis" --graph-repo ./examples/graphs --explain

# Find simple graphs
dyn-advisor recommend "simple" --graph-repo ./examples/graphs
```

### 4. Execute a Graph (Safe Mode Demo)

First, try executing without the `--run` flag:

```bash
dyn-advisor execute "Simple Rectangle Creator" --graph-repo ./examples/graphs
```

This will show the graph information but won't execute it (safe by default).

Now try with the `--run` flag:

```bash
dyn-advisor execute "Simple Rectangle Creator" --graph-repo ./examples/graphs --run
```

You'll see execution is blocked because:
1. `ALLOW_EXECUTION` is set to `false` in the default configuration
2. This is intentional for safety!

## Using with Your Own Graphs

### 1. Set Up Your Configuration

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and set your paths
nano .env  # or use your favorite editor
```

Set at minimum:
```
GRAPH_REPO_PATH=/path/to/your/dynamo/graphs
DOCS_PATH=/path/to/your/documentation
```

### 2. Index Your Graphs

```bash
dyn-advisor index
```

### 3. Get Recommendations

```bash
dyn-advisor recommend "your search query"
```

### 4. (Optional) Enable Execution

Only do this if you understand the implications and have configured Dynamo CLI:

1. Edit `.env` and set:
   ```
   ALLOW_EXECUTION=true
   DYNAMO_CLI_PATH=/path/to/DynamoSandbox.exe
   ```

2. Execute a graph:
   ```bash
   dyn-advisor recommend "your query" --run
   ```

## Safety Features

dyn-advisor has multiple layers of safety:

1. **Execution Off by Default**: `ALLOW_EXECUTION=false` by default
2. **Configuration Required**: You must set `DYNAMO_CLI_PATH`
3. **Explicit Consent**: You must use `--run` flag
4. **Full Logging**: All actions are logged
5. **No Secrets in Code**: All configuration via `.env`

All three conditions (config flag, CLI path, and runtime flag) must be met for execution to proceed.

## Next Steps

- Read the [README.md](README.md) for complete documentation
- Check example graphs in `examples/graphs/`
- Review logging output in the console
- Explore the source code in `dyn_advisor/`

## Troubleshooting

### "No graphs found"

Make sure your `GRAPH_REPO_PATH` points to a directory containing `.dyn` files.

### "Execution is disabled"

This is intentional for safety. See "Enable Execution" above if you want to enable it.

### "Dynamo CLI not found"

Set the correct path to DynamoSandbox.exe in your `.env` file.
