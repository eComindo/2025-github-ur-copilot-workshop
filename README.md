# GitHub Copilot Workshop

This is a sample repository for Github Copilot Workshop in Github Universe Recap 2025, Jakarta, Indonesia.

Using the files in this repository, we are going to create a web application for Pomodoro Technique using Python, JavaScript, HTML, and CSS.

## Installation

We need to have `uv` and `venv` installed for this project.

### uv

`uv` is an extremely fast Python package and project manager, written in Rust. Open  [this link](https://docs.astral.sh/uv/#installation) for the installation information.

### venv

`venv` is a module included with Python (version 3.3 and later) used to create isolated Python virtual environments.

After `uv` is available on your system, install `venv` to create a virtual environment for this work project. Go to the root of your project and run this command:
```bash
uv venv
```

Then, activate virtual environment:
```bash
source .venv/bin/activate
```

Note: to deactivate virtual environment:
```bash
deactivate
```

## Dependencies

Install the required Python packages using `uv`:

```bash
uv pip install -r requirements.txt
```

## Running the Application

To start the Pomodoro Timer web application:

```bash
python app.py
```

Then open your web browser and navigate to `http://127.0.0.1:5000`

## Testing

This project includes comprehensive unit and integration tests to ensure code quality and reliability.

### Installing Test Dependencies

Test dependencies are included in `requirements.txt`. If you've already installed the requirements, you have everything needed to run tests.

### Running Tests

We provide several ways to run tests:

#### Option 1: Using the Test Runner Script (Recommended)

```bash
# Run all tests with coverage report
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run tests with detailed coverage report
python run_tests.py coverage

# Run tests until first failure (useful for debugging)
python run_tests.py quick

# Run tests with verbose output
python run_tests.py verbose

# Show help for all available options
python run_tests.py help
```

#### Option 2: Using pytest directly

```bash
# Run all tests
".venv/Scripts/python.exe" -m pytest

# Run tests with coverage
".venv/Scripts/python.exe" -m pytest --cov=app --cov-report=term-missing

# Run specific test file
".venv/Scripts/python.exe" -m pytest tests/test_app.py

# Run tests with verbose output
".venv/Scripts/python.exe" -m pytest -v

# Run tests and stop on first failure
".venv/Scripts/python.exe" -m pytest -x
```

#### Option 3: Using uv (if preferred)

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing
```

### Test Structure

The test suite is organized into two main categories:

- **Unit Tests** (`tests/test_app.py`): Test individual functions and components in isolation
  - Flask route handlers
  - Data validation
  - Error handling
  - Configuration testing

- **Integration Tests** (`tests/test_integration.py`): Test complete user workflows and system interactions
  - End-to-end session logging workflows
  - File system operations
  - Data persistence across requests
  - Error recovery and data integrity

### Coverage Reports

After running tests with coverage, you can view detailed coverage reports:

- **Terminal Report**: Shows coverage summary in the terminal
- **HTML Report**: Detailed interactive report generated in `htmlcov/index.html`

To view the HTML coverage report:
```bash
# On Windows
start htmlcov/index.html

# On macOS
open htmlcov/index.html

# On Linux
xdg-open htmlcov/index.html
```

### Test Configuration

Test configuration is managed in `pyproject.toml` with the following features:

- **Automatic test discovery**: Finds all test files matching `test_*.py`
- **Coverage reporting**: Tracks code coverage and generates reports
- **Minimum coverage threshold**: Tests fail if coverage drops below 85%
- **Organized test markers**: Tests can be categorized and run selectively

### Writing New Tests

When adding new features, please include corresponding tests:

1. **Unit tests**: Add to `tests/test_app.py` for testing individual functions
2. **Integration tests**: Add to `tests/test_integration.py` for testing complete workflows
3. **Follow naming conventions**: Test functions should start with `test_`
4. **Use descriptive names**: Test names should clearly describe what is being tested

Example test structure:
```python
def test_feature_name_expected_behavior():
    """Test description of what this test verifies."""
    # Arrange
    setup_test_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### Continuous Integration

The test suite is designed to be run in CI/CD pipelines. All tests should pass before merging code changes.