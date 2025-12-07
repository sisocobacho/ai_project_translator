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
