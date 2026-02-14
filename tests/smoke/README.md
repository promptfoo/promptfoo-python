# Smoke Tests

These smoke tests verify that the core promptfoo CLI functionality works correctly through the Python wrapper.

## What are Smoke Tests?

Smoke tests are high-level integration tests that verify the most critical functionality works end-to-end. They:

- Run against the actual installed CLI via the Python wrapper (using either global promptfoo or npx)
- Test the Python wrapper integration with the Node.js CLI
- Use the `echo` provider to avoid external API dependencies
- Verify command-line arguments, file I/O, and output formats
- Check exit codes and error handling

## Running Smoke Tests

```bash
# Run all smoke tests
pytest tests/smoke/

# Run with verbose output
pytest tests/smoke/ -v

# Run a specific test class
pytest tests/smoke/test_smoke.py::TestEvalCommand

# Run a specific test
pytest tests/smoke/test_smoke.py::TestEvalCommand::test_basic_eval
```

## Test Structure

- `test_smoke.py` - Main smoke test suite
- `fixtures/` - Test configuration files
  - `configs/` - YAML configuration files for testing

## Test Coverage

### Basic CLI Operations
- Version flag (`--version`)
- Help output (`--help`, `eval --help`)
- Unknown command handling
- Missing file error handling

### Eval Command
- Basic evaluation with echo provider
- Output formats (JSON, YAML, CSV)
- Command-line flags (`--max-concurrency`, `--repeat`, `--verbose`)
- Cache control (`--no-cache`)

### Exit Codes
- Exit code 0 for success
- Exit code 100 for assertion failures
- Exit code 1 for configuration errors

### Echo Provider
- Basic prompt echoing
- Variable substitution
- Multiple variable handling

### Assertions
- `contains` assertion
- `icontains` assertion (case-insensitive)
- Multiple assertions per test
- Failing assertion behavior

## Why Echo Provider?

The `echo` provider is perfect for smoke tests because:

1. **No external dependencies** - Doesn't require API keys or network calls
2. **Deterministic** - Always returns the same output for the same input
3. **Fast** - No network latency
4. **Predictable** - Easy to write assertions against

## Adding New Smoke Tests

1. Create a new test config in `fixtures/configs/` if needed
2. Add test methods to the appropriate test class in `test_smoke.py`
3. Use the `run_promptfoo()` helper to execute CLI commands
4. Make assertions on stdout, stderr, exit codes, and output files

## Notes

- Smoke tests run slower than unit tests (they spawn subprocesses)
- They require Node.js and promptfoo to be installed
- They test the integration between Python and Node.js
- They should be kept focused on critical functionality
