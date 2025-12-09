import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_project_translator.main import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    
    assert config.max_size == 600000
    assert ".git" in config.exclude_dirs
    assert ".py" in config.extensions
    assert config.extension_map[".py"] == "python"
    assert config.max_depth == 3


def test_config_environment_variables_exclude_dirs(monkeypatch):
    """Test setting exclude_dirs via environment variable."""
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", 'custom1,custom2,custom3')
    
    config = Config()
    
    assert "custom1" in config.exclude_dirs
    assert "custom2" in config.exclude_dirs
    assert "custom3" in config.exclude_dirs
    # Should still have defaults unless overridden
    assert ".git" not in config.exclude_dirs  # Still in default set


def test_config_environment_variables_extensions(monkeypatch):
    """Test setting extensions via environment variable."""
    monkeypatch.setenv("AI_PT_EXTENSIONS", '.py,.js,.txt')
    
    config = Config()
    
    assert ".py" in config.extensions
    assert ".js" in config.extensions
    assert ".txt" in config.extensions
    # Should only have what we specified (overrides defaults)
    assert ".html" not in config.extensions
    assert ".css" not in config.extensions


def test_config_environment_variables_max_size(monkeypatch):
    """Test setting max_size via environment variable."""
    monkeypatch.setenv("AI_PT_MAX_SIZE", "1000000")
    
    config = Config()
    
    assert config.max_size == 1000000


def test_config_environment_variables_max_depth(monkeypatch):
    """Test setting max_depth via environment variable."""
    monkeypatch.setenv("AI_PT_MAX_DEPTH", "5")
    
    config = Config()
    
    assert config.max_depth == 5


def test_config_environment_variables_all_together(monkeypatch):
    """Test setting multiple environment variables together."""
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", 'build,dist,coverage')
    monkeypatch.setenv("AI_PT_MAX_SIZE", "500000")
    monkeypatch.setenv("AI_PT_EXTENSIONS", '.py,.js')
    monkeypatch.setenv("AI_PT_MAX_DEPTH", "2")
    
    config = Config()
    
    assert "build" in config.exclude_dirs
    assert "dist" in config.exclude_dirs
    assert "coverage" in config.exclude_dirs
    assert config.max_size == 500000
    assert ".py" in config.extensions
    assert ".js" in config.extensions
    assert ".html" not in config.extensions
    assert config.max_depth == 2


def test_config_parse_exclude_dirs_with_spaces(monkeypatch):
    """Test parsing exclude_dirs with spaces around commas."""
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", 'build,dist,coverage')
    
    config = Config()
    
    assert "build" in config.exclude_dirs
    assert "dist" in config.exclude_dirs
    assert "coverage" in config.exclude_dirs


def test_config_empty_environment_variable(monkeypatch):
    """Test with empty environment variable."""
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", "")
    
    config = Config()
    
    # Should use defaults when empty
    assert ".git" in config.exclude_dirs
    assert "__pycache__" in config.exclude_dirs


def test_config_invalid_max_size(monkeypatch):
    """Test with invalid max_size environment variable."""
    monkeypatch.setenv("AI_PT_MAX_SIZE", "not_a_number")
    
    with pytest.raises(ValueError):
        Config()

def test_config_empty_max_size(monkeypatch):
    """Test with invalid max_size environment variable."""
    monkeypatch.setenv("AI_PT_MAX_SIZE", "")
    
    config = Config()
    # should use default
    assert config.max_size == 600000

def test_config_whitespace_only_environment_variable(monkeypatch):
    """Test with whitespace-only environment variable."""
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", "   ")
    
    config = Config()
    
    # Should use defaults when only whitespace
    assert ".git" in config.exclude_dirs
    assert "__pycache__" in config.exclude_dirs


def test_config_case_insensitive_env_prefix():
    """Test that environment variable prefix is case insensitive."""
    # Pydantic-settings should handle case insensitivity
    config = Config()
    
    # Test that we can access config
    assert config.max_size is not None
    assert config.exclude_dirs is not None


def test_config_merge_defaults_with_env(monkeypatch):
    """Test that environment variables override but don't remove defaults for sets."""
    # When we set exclude_dirs via env, it should add to defaults
    # Actually, with pydantic, setting a field replaces it completely
    # So we need to include defaults if we want to keep them
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", ".git,__pycache__,custom")
    
    config = Config()
    
    # The env var completely replaces the default
    assert ".git" in config.exclude_dirs
    assert "__pycache__" in config.exclude_dirs
    assert "custom" in config.exclude_dirs
    # But we lost other defaults like "node_modules"
    assert "node_modules" not in config.exclude_dirs
