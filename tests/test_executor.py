"""
Tests for the executor module.
"""

from dyn_advisor.executor import DynamoExecutor


def test_execution_disabled_by_default():
    """Test that execution is disabled by default."""
    executor = DynamoExecutor('/fake/path', allow_execution=False)

    assert not executor.can_execute()


def test_execution_requires_cli_path():
    """Test that execution requires a valid CLI path."""
    executor = DynamoExecutor('', allow_execution=True)

    assert not executor.can_execute()


def test_execution_blocked_without_allow_flag():
    """Test that execution is blocked without ALLOW_EXECUTION."""
    executor = DynamoExecutor('/fake/path', allow_execution=False)

    graph = {
        'name': 'Test Graph',
        'filepath': '/fake/path/test.dyn'
    }

    result = executor.execute_graph(graph, run_flag=True)

    assert not result['success']
    assert not result['executed']
    assert 'ALLOW_EXECUTION' in result['message']


def test_execution_blocked_without_run_flag():
    """Test that execution is blocked without --run flag."""
    executor = DynamoExecutor('/fake/path', allow_execution=True)

    graph = {
        'name': 'Test Graph',
        'filepath': '/fake/path/test.dyn'
    }

    result = executor.execute_graph(graph, run_flag=False)

    assert not result['success']
    assert not result['executed']
    assert '--run flag' in result['message']


def test_execution_requires_existing_cli():
    """Test that execution requires an existing CLI executable."""
    executor = DynamoExecutor('/nonexistent/dynamo', allow_execution=True)

    assert not executor.can_execute()

    graph = {
        'name': 'Test Graph',
        'filepath': '/fake/path/test.dyn'
    }

    result = executor.execute_graph(graph, run_flag=True)

    assert not result['success']
    assert not result['executed']
    assert 'not configured' in result['message']
