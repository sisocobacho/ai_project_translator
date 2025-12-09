import sys
from pathlib import Path
import click.testing

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_project_translator import main


def test_cli_without_arguments():
    """Test CLI without any arguments (default current directory)."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli)

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert "CODE FILES:" in result.output


def test_cli_with_path_argument(sample_project_structure):
    """Test CLI with a path argument."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(sample_project_structure)])

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert sample_project_structure.name in result.output


def test_cli_single_file_analysis(temp_dir):
    """Test CLI with a single file path."""
    # Create a Python file
    file_path = temp_dir / "test.py"
    file_content = "def hello():\n    return 'world'\n"
    file_path.write_text(file_content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path)])

    assert result.exit_code == 0
    assert "Single File Analysis:" in result.output
    assert "File: test.py" in result.output
    assert "FILE CONTENT:" in result.output
    assert "```python" in result.output
    assert file_content in result.output
    assert "Project Structure:" not in result.output
    assert "CODE FILES:" not in result.output


def test_cli_single_file_with_framework(temp_dir):
    """Test CLI with a single file and framework option."""
    file_path = temp_dir / "test.py"
    file_content = "def hello():\n    return 'world'\n"
    file_path.write_text(file_content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path), "--framework", "FastAPI"])

    assert result.exit_code == 0
    assert "Single File Analysis:" in result.output
    assert "File: test.py" in result.output
    assert "**Framework:** FastAPI" in result.output
    assert "```python" in result.output


def test_cli_single_file_with_question(temp_dir):
    """Test CLI with a single file and question option."""
    file_path = temp_dir / "test.py"
    file_content = "def hello():\n    return 'world'\n"
    file_path.write_text(file_content)

    test_question = "Can you improve this function?"
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path), "--question", test_question])

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    assert test_question in result.output
    assert "Single File Analysis:" in result.output
    assert "File: test.py" in result.output


def test_cli_single_file_unsupported_extension(temp_dir):
    """Test CLI with a single file that has unsupported extension."""
    file_path = temp_dir / "test.xyz"
    file_content = "some content"
    file_path.write_text(file_content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path)])

    assert result.exit_code == 0
    assert "Error:" in result.output
    assert "is not a supported code file type" in result.output
    assert "Supported extensions:" in result.output


def test_cli_single_file_large_file(temp_dir):
    """Test CLI with a large single file."""
    file_path = temp_dir / "large.py"
    # Create a file larger than default max_size
    content = "x" * (main.config.max_size + 1000)
    file_path.write_text(content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path)])

    assert result.exit_code == 0
    assert "Skipping large file:" in result.output
    assert "File too large" in result.output


def test_cli_single_file_large_file_with_include_large(temp_dir):
    """Test CLI with a large single file using --include-large."""
    file_path = temp_dir / "large.py"
    content = "x" * (main.config.max_size + 1000)
    file_path.write_text(content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path), "--include-large"])

    assert result.exit_code == 0
    assert "Single File Analysis:" in result.output
    assert "File: large.py" in result.output
    # Should show the file info even if large
    assert "*Note: File too large" in result.output


def test_cli_single_file_output_options_ignored(temp_dir):
    """Test that --output option is ignored for single file analysis."""
    file_path = temp_dir / "test.py"
    file_content = "def hello():\n    return 'world'\n"
    file_path.write_text(file_content)

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(file_path), "--output", "structure"])

    assert result.exit_code == 0
    # Should show single file analysis regardless of output option
    assert "Single File Analysis:" in result.output
    assert "Project Structure:" not in result.output  # Should not show structure


def test_cli_with_framework_option(sample_project_structure):
    """Test CLI with framework option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli, [str(sample_project_structure), "--framework", "FastAPI"]
    )

    assert result.exit_code == 0
    assert "**Framework:** FastAPI" in result.output


def test_cli_with_question_option(sample_project_structure):
    """Test CLI with question option."""
    test_question = "Can you help me refactor this code to use async/await?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [str(sample_project_structure), "--question", test_question],
    )

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    assert test_question in result.output
    # Question should be at the beginning
    assert result.output.startswith("**Question:**")


def test_cli_with_question_and_framework(sample_project_structure):
    """Test CLI with both question and framework options."""
    test_question = "How can I improve error handling in this Flask app?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [
            str(sample_project_structure),
            "--question",
            test_question,
            "--framework",
            "Flask",
        ],
    )

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    assert test_question in result.output
    assert "**Framework:** Flask" in result.output
    # Question should come before framework in files
    assert result.output.find("**Question:**") < result.output.find(
        "**Framework:** Flask"
    )


def test_cli_with_empty_question(sample_project_structure):
    """Test CLI with empty question string."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [str(sample_project_structure), "--question", ""],
    )

    assert result.exit_code == 0
    # Empty question should not be included
    assert "**Question:**" not in result.output


def test_cli_with_question_without_punctuation(sample_project_structure):
    """Test CLI with question that doesn't end with punctuation."""
    test_question = "Can you add tests for this function"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [str(sample_project_structure), "--question", test_question],
    )

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    # Should add period at the end
    assert f"{test_question}." in result.output


def test_cli_with_question_with_punctuation(sample_project_structure):
    """Test CLI with question that already has punctuation."""
    test_question = "What's wrong with this code?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [str(sample_project_structure), "--question", test_question],
    )

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    # Should keep the original punctuation
    assert test_question in result.output
    assert (
        f"{test_question}?" not in result.output
    )  # Should not double the question mark


def test_cli_with_output_structure_only(sample_project_structure):
    """Test CLI with structure-only output."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli, [str(sample_project_structure), "--output", "structure"]
    )

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert "CODE FILES:" not in result.output


def test_cli_with_output_files_only(sample_project_structure):
    """Test CLI with files-only output."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli, [str(sample_project_structure), "--output", "files"]
    )

    assert result.exit_code == 0
    assert "Project Structure:" not in result.output
    assert "CODE FILES:" in result.output


def test_cli_with_nonexistent_path():
    """Test CLI with non-existent path."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, ["/nonexistent/path"])

    assert result.exit_code == 0
    assert "Error: Path" in result.output
    assert "does not exist" in result.output


def test_cli_no_copy_option(sample_project_structure, mock_clipboard):
    """Test CLI with --no-copy option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(sample_project_structure), "--no-copy"])

    assert result.exit_code == 0
    mock_clipboard.copy.assert_not_called()


def test_cli_include_large_option(sample_project_structure, large_file):
    """Test CLI with --include-large option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.cli,
        [str(sample_project_structure), "--include-large", "--max-size", "100"],
    )

    assert result.exit_code == 0
    # Should mention large files
    assert "too large" in result.output


def test_cli_show_config_option():
    """Test CLI with --show-config option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, ["--show-config"])

    assert result.exit_code == 0
    assert "Current Configuration:" in result.output
    assert "Exclude directories:" in result.output
    assert "Max file size:" in result.output
    assert "Environment variables used:" in result.output


def test_cli_with_environment_variables(monkeypatch, sample_project_structure):
    """Test CLI with environment variables."""
    # Set environment variables
    monkeypatch.setenv("AI_PT_EXCLUDE_DIRS", "tests,docs")
    monkeypatch.setenv("AI_PT_EXCLUDE_FILES", "test.py,requirements.txt")
    monkeypatch.setenv("AI_PT_MAX_SIZE", "100000")

    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, [str(sample_project_structure)])

    assert result.exit_code == 0
    # The tool should use the environment variables
    # (Actual behavior depends on implementation)


def test_cli_whit_exclude_files_option(temp_dir):
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli)
    assert result.exit_code == 0
    assert "pyproject.toml" in result.output
    result = runner.invoke(
        main.cli, [str(temp_dir), "--exclude-files", "pyproject.toml"]
    )
    assert result.exit_code == 0
    assert "pyproject.toml" not in result.output
