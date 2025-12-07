import sys
from pathlib import Path
import click.testing

sys.path.insert(0, str(Path(__file__).parent.parent))

import main


def test_cli_without_arguments():
    """Test CLI without any arguments (default current directory)."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project)

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert "CODE FILES:" in result.output


def test_cli_with_path_argument(sample_project_structure):
    """Test CLI with a path argument."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project, [str(sample_project_structure)])

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert sample_project_structure.name in result.output


def test_cli_with_framework_option(sample_project_structure):
    """Test CLI with framework option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project, [str(sample_project_structure), "--framework", "FastAPI"]
    )

    assert result.exit_code == 0
    assert "**Framework:** FastAPI" in result.output


def test_cli_with_question_option(sample_project_structure):
    """Test CLI with question option."""
    test_question = "Can you help me refactor this code to use async/await?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
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
        main.analyze_project,
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
    assert result.output.find("**Question:**") < result.output.find("**Framework:** Flask")


def test_cli_with_empty_question(sample_project_structure):
    """Test CLI with empty question string."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
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
        main.analyze_project,
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
        main.analyze_project,
        [str(sample_project_structure), "--question", test_question],
    )

    assert result.exit_code == 0
    assert "**Question:**" in result.output
    # Should keep the original punctuation
    assert test_question in result.output
    assert f"{test_question}?" not in result.output  # Should not double the question mark


def test_cli_with_output_structure_only(sample_project_structure):
    """Test CLI with structure-only output."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project, [str(sample_project_structure), "--output", "structure"]
    )

    assert result.exit_code == 0
    assert "Project Structure:" in result.output
    assert "CODE FILES:" not in result.output


def test_cli_with_output_files_only(sample_project_structure):
    """Test CLI with files-only output."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project, [str(sample_project_structure), "--output", "files"]
    )

    assert result.exit_code == 0
    assert "Project Structure:" not in result.output
    assert "CODE FILES:" in result.output


def test_cli_with_nonexistent_path():
    """Test CLI with non-existent path."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project, ["/nonexistent/path"])

    assert result.exit_code == 0
    assert "Error: Path" in result.output
    assert "does not exist" in result.output


def test_cli_with_file_instead_of_directory(temp_dir):
    """Test CLI with a file instead of directory."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("test")

    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project, [str(file_path)])

    assert result.exit_code == 0
    assert "Error: " in result.output
    assert "is not a directory" in result.output


def test_cli_no_copy_option(sample_project_structure, mock_clipboard):
    """Test CLI with --no-copy option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project, [str(sample_project_structure), "--no-copy"]
    )

    assert result.exit_code == 0
    mock_clipboard.copy.assert_not_called()


def test_cli_include_large_option(sample_project_structure, large_file):
    """Test CLI with --include-large option."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
        [str(sample_project_structure), "--include-large", "--max-size", "100"],
    )

    assert result.exit_code == 0
    # Should mention large files
    assert "too large" in result.output
