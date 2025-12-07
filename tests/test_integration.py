import sys
from pathlib import Path
import click.testing

sys.path.insert(0, str(Path(__file__).parent.parent))

import main


def test_integration_full_workflow(sample_project_structure, mock_clipboard):
    """Test the full integration workflow."""
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
        [str(sample_project_structure), "--framework", "TestFramework"],
    )

    assert result.exit_code == 0

    # Check output structure
    output = result.output
    assert "**Project Structure:**" in output
    assert "Path:" in output
    assert sample_project_structure.name in output
    assert "CODE FILES:" in output

    # Check that files are formatted correctly
    assert "**Framework:** TestFramework" in output
    assert "**File:** README.md" in output
    assert "```markdown" in output
    assert "# Test Project" in output

    # Check clipboard was called
    mock_clipboard.copy.assert_called_once()
    clipboard_content = mock_clipboard.copy.call_args[0][0]
    assert "**Project Structure:**" in clipboard_content
    assert "**Framework:** TestFramework" in clipboard_content


def test_integration_with_question(sample_project_structure, mock_clipboard):
    """Test integration workflow with question."""
    test_question = "How can I improve the structure of this project?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
        [
            str(sample_project_structure),
            "--question",
            test_question,
            "--framework",
            "Django",
        ],
    )

    assert result.exit_code == 0

    # Check output structure
    output = result.output
    assert "**Question:**" in output
    assert test_question in output
    assert "**Framework:** Django" in output
    assert "**Project Structure:**" in output
    assert "CODE FILES:" in output

    # Question should be at the beginning
    assert output.startswith("**Question:**")

    # Check clipboard was called
    mock_clipboard.copy.assert_called_once()
    clipboard_content = mock_clipboard.copy.call_args[0][0]
    assert "**Question:**" in clipboard_content
    assert test_question in clipboard_content


def test_integration_empty_directory(temp_dir, mock_clipboard):
    """Test integration with an empty directory."""
    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project, [str(temp_dir)])

    assert result.exit_code == 0
    assert "No code files found" in result.output


def test_integration_with_permission_error(mocker, temp_dir):
    """Test integration when directory cannot be accessed."""
    # Mock os.listdir to raise PermissionError
    mocker.patch("os.listdir", side_effect=PermissionError("Access denied"))

    runner = click.testing.CliRunner()
    result = runner.invoke(main.analyze_project, [str(temp_dir)])

    # Should still exit successfully but with minimal output
    assert result.exit_code == 0
    assert "No code files found in the specified directory." in result.output


def test_integration_question_only_with_structure(sample_project_structure, mock_clipboard):
    """Test integration with question and structure only output."""
    test_question = "What do you think of this project structure?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
        [
            str(sample_project_structure),
            "--question",
            test_question,
            "--output",
            "structure",
        ],
    )

    assert result.exit_code == 0
    output = result.output
    
    # Should have question
    assert "**Question:**" in output
    assert test_question in output
    
    # Should have structure
    assert "**Project Structure:**" in output
    
    # Should NOT have code files section
    assert "CODE FILES:" not in output


def test_integration_question_only_with_files(sample_project_structure, mock_clipboard):
    """Test integration with question and files only output."""
    test_question = "Can you review these code files?"
    runner = click.testing.CliRunner()
    result = runner.invoke(
        main.analyze_project,
        [
            str(sample_project_structure),
            "--question",
            test_question,
            "--output",
            "files",
        ],
    )

    assert result.exit_code == 0
    output = result.output
    
    # Should have question
    assert "**Question:**" in output
    assert test_question in output
    
    # Should NOT have structure
    assert "**Project Structure:**" not in output
    
    # Should have code files section
    assert "CODE FILES:" in output
