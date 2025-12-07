import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


def test_config_exists():
    """Test that Config class exists and has required attributes."""
    assert hasattr(main, "Config")
    assert hasattr(main, "config")
    assert isinstance(main.config, main.Config)


def test_config_defaults():
    """Test default configuration values."""
    config = main.Config()

    assert config.max_size == 600000

    # Check some expected excluded directories
    expected_excludes = {".git", "__pycache__", "node_modules", ".venv"}
    assert expected_excludes.issubset(config.exclude_dirs)

    # Check some expected extensions
    expected_extensions = {".py", ".js", ".html", ".css", ".json", ".md"}
    assert expected_extensions.issubset(config.extensions)

    # Check extension map
    assert config.extension_map[".py"] == "python"
    assert config.extension_map[".js"] == "javascript"
    assert config.extension_map[".md"] == "markdown"
    assert config.extension_map.get(".xyz", "text") == "text"


def test_config_instance():
    """Test that the global config instance works correctly."""
    assert main.config.max_size == 600000
    assert ".git" in main.config.exclude_dirs
    assert ".py" in main.config.extensions
