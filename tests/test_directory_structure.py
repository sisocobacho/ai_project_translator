import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import main


def test_get_directory_structure_empty_dir(temp_dir):
    """Test directory structure for an empty directory."""
    structure = main.get_directory_structure(temp_dir)

    assert len(structure) == 1
    assert structure[0] == f"{temp_dir.name}/"


def test_get_directory_structure_with_files(temp_dir):
    """Test directory structure with files."""
    # Create some files
    (temp_dir / "file1.txt").write_text("test")
    (temp_dir / "file2.py").write_text("print('hello')")

    structure = main.get_directory_structure(temp_dir)

    assert len(structure) >= 3  # root + 2 files
    assert any("file1.txt" in line for line in structure)
    assert any("file2.py" in line for line in structure)


def test_get_directory_structure_with_nested_dirs(temp_dir):
    """Test directory structure with nested directories."""
    # Create nested structure
    (temp_dir / "src" / "utils").mkdir(parents=True)
    (temp_dir / "src" / "utils" / "helpers.py").write_text("def help():\n    pass")

    structure = main.get_directory_structure(temp_dir)

    # Check that nested structure is included
    structure_text = "\n".join(structure)
    assert "src/" in structure_text
    assert "utils/" in structure_text
    assert "helpers.py" in structure_text


def test_get_directory_structure_excludes_dirs(temp_dir):
    """Test that excluded directories are not included."""
    # Create excluded directory
    (temp_dir / "__pycache__").mkdir()
    (temp_dir / "__pycache__" / "test.pyc").write_text("binary")

    # Create regular directory
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("print('hello')")

    structure = main.get_directory_structure(temp_dir)
    structure_text = "\n".join(structure)

    # Should not include __pycache__
    assert "__pycache__" not in structure_text
    # Should include regular directory
    assert "src/" in structure_text
    assert "main.py" in structure_text


def test_get_directory_structure_max_depth(temp_dir):
    """Test that max_depth parameter works correctly."""
    # Create deeply nested structure
    current = temp_dir
    for i in range(5):
        current = current / f"dir{i}"
        current.mkdir()
        (current / f"file{i}.txt").write_text(f"content {i}")

    # Test with max_depth=2
    structure = main.get_directory_structure(temp_dir, max_depth=2)
    structure_text = "\n".join(structure)

    # Should show up to 2 levels deep
    assert "dir0/" in structure_text
    assert "dir1/" in structure_text
    # Should not show beyond depth 2
    assert "dir3/" not in structure_text
