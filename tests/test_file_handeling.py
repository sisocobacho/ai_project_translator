import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import main


def test_get_file_extension_language():
    """Test mapping file extensions to language names."""
    test_cases = [
        ("test.py", "python"),
        ("script.js", "javascript"),
        ("component.jsx", "jsx"),
        ("style.css", "css"),
        ("index.html", "html"),
        ("config.json", "json"),
        ("README.md", "markdown"),
        ("unknown.xyz", "text"),  # Unknown extension
    ]

    for filename, expected_language in test_cases:
        result = main.get_file_extension_language(filename)
        assert result == expected_language, (
            f"Failed for {filename}: {result} != {expected_language}"
        )


def test_read_file_content_success(temp_dir):
    """Test reading file content successfully."""
    file_path = temp_dir / "test.txt"
    expected_content = "Hello, World!\nThis is a test."
    file_path.write_text(expected_content)

    content, error = main.read_file_content(file_path)

    assert content == expected_content
    assert error is None


def test_read_file_content_too_large(large_file):
    """Test reading a file that exceeds size limit."""
    content, error = main.read_file_content(large_file, max_size=5000)

    assert content is None
    assert error is not None
    assert "too large" in error
    assert "10000" in error  # Should mention the file size


def test_read_file_content_nonexistent():
    """Test reading a non-existent file."""
    content, error = main.read_file_content(Path("/nonexistent/file.txt"))

    assert content is None
    assert error is not None
    assert "Error reading file" in error


def test_get_code_files_with_content(sample_project_structure):
    """Test finding code files with their content."""
    code_files = main.get_code_files_with_content(
        sample_project_structure, max_file_size=60000000
    )

    # Should find all code files (excluding excluded directories)
    file_paths = [f["path"] for f in code_files]
    assert "README.md" in file_paths
    assert "pyproject.toml" in file_paths
    assert "src/main.py" in file_paths
    assert "tests/test_main.py" in file_paths

    # Should not include files in excluded directories
    assert not any("__pycache__" in f["path"] for f in code_files)

    # Check that content was read
    for file_info in code_files:
        if "README.md" in file_info["path"]:
            assert file_info["content"] == "# Test Project\n\nThis is a test project."
            assert file_info["language"] == "markdown"
        elif "src/main.py" in file_info["path"]:
            assert "def hello():" in file_info["content"]
            assert file_info["language"] == "python"


def test_get_code_files_with_empty_dir(temp_dir):
    """Test finding code files in an empty directory."""
    code_files = main.get_code_files_with_content(temp_dir)
    assert len(code_files) == 0


def test_get_code_files_with_custom_extensions(temp_dir):
    """Test finding code files with custom extensions."""
    # Create files with different extensions
    (temp_dir / "test.py").write_text("python code")
    (temp_dir / "test.txt").write_text("text file")
    (temp_dir / "test.xyz").write_text("unknown extension")

    # Test with only .py extension
    code_files = main.get_code_files_with_content(temp_dir, extensions={".py"})

    file_paths = [f["path"] for f in code_files]
    assert "test.py" in file_paths
    assert "test.txt" not in file_paths
    assert "test.xyz" not in file_paths


def test_format_file_for_ai():
    """Test formatting file information for AI context."""
    file_info = {
        "path": "src/main.py",
        "language": "python",
        "content": "def hello():\n    return 'world'",
        "error": None,
    }

    # Without framework
    result = main.format_file_for_ai(file_info)
    assert "**File:** src/main.py" in result
    assert "```python" in result
    assert "def hello():" in result
    assert "**Framework:**" not in result

    # With framework
    result = main.format_file_for_ai(file_info, framework="Flask")
    assert "**Framework:** Flask" in result
    assert "**File:** src/main.py" in result
    assert "```python" in result


def test_format_file_for_ai_with_error():
    """Test formatting file information when there's an error."""
    file_info = {
        "path": "large_file.py",
        "language": "python",
        "content": None,
        "error": "File too large (10000 bytes), skipping content",
    }

    result = main.format_file_for_ai(file_info)
    assert "**File:** large_file.py" in result
    assert "*Note: File too large" in result
    assert "```python" not in result
    assert "**Purpose:**" not in result
