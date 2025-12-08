import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_project_structure(temp_dir):
    """Create a sample project structure for testing."""
    # Create directories
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()

    # Create files
    (temp_dir / "README.md").write_text("# Test Project\n\nThis is a test project.")
    (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (temp_dir / ".gitignore").write_text("*.pyc\n__pycache__/\n")

    # Create source files
    (temp_dir / "src" / "__init__.py").write_text("")
    (temp_dir / "src" / "main.py").write_text("def hello():\n    return 'world'\n")

    # Create test files
    (temp_dir / "tests" / "__init__.py").write_text("")
    (temp_dir / "tests" / "test_main.py").write_text(
        "import pytest\n\ndef test_hello():\n    pass\n"
    )

    # Create excluded directory
    (temp_dir / "__pycache__").mkdir()
    (temp_dir / "__pycache__" / "test.pyc").write_text("binary content")

    return temp_dir


@pytest.fixture
def large_file(temp_dir):
    """Create a large file for testing size limits."""
    large_file_path = temp_dir / "large_file.py"
    # Create a file larger than default max_size (5000 bytes)
    content = "x" * 10000
    large_file_path.write_text(content)
    return large_file_path


@pytest.fixture
def mock_clipboard(mocker):
    """Mock the pyperclip module."""
    return mocker.patch("ai_project_translator.main.pyperclip", autospec=True)
