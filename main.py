import os
import click
from pathlib import Path
import pyperclip


class Config:
    max_size = 600000
    exclude_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".vscode",
        ".idea",
        "venv",
        "env",
        ".venv",
        ".ruff_cache",
        "htmlcov",
        ".pytest_cache",
    }
    extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".yml",
        ".toml",
        ".md",
        ".txt",
    }
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".yml": "yaml",
        ".md": "markdown",
        ".txt": "text",
        ".sh": "bash",
        ".bash": "bash",
        ".php": "php",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".cs": "csharp",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".sql": "sql",
    }


config = Config()


def format_question_for_output(question):
    """Format the question for inclusion in the output."""
    if not question:
        return ""
    
    # Clean up the question - remove extra whitespace
    question = question.strip()
    
    # If question doesn't end with punctuation, add a period
    if question and question[-1] not in ['.', '!', '?', ':']:
        question = question + '.'
    
    return question


def get_directory_structure(startpath, exclude_dirs=None, max_depth=3):
    """
    Generate a tree-like structure of the directory
    """
    if exclude_dirs is None:
        exclude_dirs = config.exclude_dirs
    structure = []

    def build_tree(path, prefix="", depth=0):
        if depth > max_depth:
            return

        try:
            contents = sorted(os.listdir(path))
        except PermissionError:
            return

        files = []
        dirs = []

        for item in contents:
            if item in exclude_dirs:
                continue
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)

        # Add directories
        for i, directory in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and (len(files) == 0)
            connector = "└── " if is_last_dir else "├── "
            structure.append(f"{prefix}{connector}{directory}/")

            new_prefix = prefix + ("    " if is_last_dir else "│   ")
            build_tree(os.path.join(path, directory), new_prefix, depth + 1)

        # Add files
        for i, file in enumerate(files):
            is_last = i == len(files) - 1
            connector = "└── " if is_last else "├── "
            structure.append(f"{prefix}{connector}{file}")

    structure.append(os.path.basename(startpath) + "/")
    build_tree(startpath)
    return structure


def get_file_extension_language(file_path):
    """
    Map file extensions to language names for code blocks
    """
    extension_map = config.extension_map
    ext = Path(file_path).suffix.lower()
    return extension_map.get(ext, "text")


def read_file_content(file_path, max_size=config.max_size):
    """
    Read file content with size limitation
    """
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return None, f"File too large ({file_size} bytes), skipping content"

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def get_code_files_with_content(
    startpath, extensions=None, max_file_size=config.max_size
):
    """
    Find all code files in the directory and read their content
    """
    if extensions is None:
        extensions = config.extensions

    code_files = []
    exclude_dirs = config.exclude_dirs
    for root, dirs, files in os.walk(startpath):
        # Skip common excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = Path(root) / file
            if any(file.endswith(ext) for ext in extensions):
                relative_path = os.path.relpath(file_path, startpath)
                language = get_file_extension_language(file)
                content, error = read_file_content(file_path, max_file_size)

                code_files.append(
                    {
                        "path": relative_path,
                        "full_path": file_path,
                        "language": language,
                        "content": content,
                        "error": error,
                        "size": file_path.stat().st_size if file_path.exists() else 0,
                    }
                )
    return sorted(code_files, key=lambda x: x["path"])


def format_file_for_ai(file_info, framework=None):
    """
    Format a single file in the recommended AI context format
    """
    output = []

    if framework:
        output.append(f"**Framework:** {framework}")

    output.append(f"**File:** {file_info['path']}")
    output.append("")

    if file_info["error"]:
        output.append(f"*Note: {file_info['error']}*")
        output.append("")
    elif file_info["content"] is not None:
        output.append(f"```{file_info['language']}")
        output.append(file_info["content"])
        output.append("```")
        output.append("")
    else:
        output.append("*No content available*")

    return "\n".join(output)


def copy_to_clipboard(content, verbose=True):
    """
    Copy content to clipboard with error handling
    """
    try:
        pyperclip.copy(content)
        if verbose:
            click.echo("✅ Output copied to clipboard!")
        return True
    except Exception as e:
        if verbose:
            click.echo(f"⚠️  Could not copy to clipboard: {str(e)}")
            click.echo("Output has been printed above. You can copy it manually.")
        return False


@click.command()
@click.argument("path", required=False, default=os.getcwd())
@click.option(
    "--framework", "-f", help="Specify the framework (e.g., Fastapi, React, Django)"
)
@click.option(
    "--question",
    "-q",
    help="Include a question to ask the AI at the beginning of the output",
)
@click.option(
    "--max-size",
    "-m",
    default=config.max_size,
    help="Maximum file size to read (bytes)",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["structure", "files", "both"]),
    default="both",
    help="Output format",
)
@click.option(
    "--include-large",
    "-l",
    is_flag=True,
    help="Include large files (content will be skipped)",
)
@click.option("--no-copy", is_flag=True, help="Do not copy to clipboard (print only)")
def analyze_project(path, framework, question, max_size, output, include_large, no_copy):
    """
    Analyze a project directory and return its structure with code content in AI-friendly format.

    PATH: Project directory path (default: current directory)
    """
    startpath = Path(path).resolve()
    startpath_name = Path(path).name

    if not startpath.exists():
        click.echo(f"Error: Path '{path}' does not exist")
        return

    if not startpath.is_dir():
        click.echo(f"Error: '{path}' is not a directory")
        return

    # all what is going to be printed
    all_output = []

    # Add the question at the beginning if provided
    if question:
        formatted_question = format_question_for_output(question)
        all_output.append("**Question:**")
        all_output.append(f"{formatted_question}")
        all_output.append("")

    if output in ["structure", "both"]:
        all_output.append("**Project Structure:**")
        all_output.append(f"Path: {startpath_name}")
        all_output.append("")

        structure = get_directory_structure(startpath)
        all_output.extend(structure)
        all_output.append("")

    if output in ["files", "both"]:
        code_files = get_code_files_with_content(startpath, max_file_size=max_size)

        if not code_files:
            click.echo("No code files found in the specified directory.")
            return

        all_output.append("=" * 80)
        all_output.append("CODE FILES:")
        all_output.append("=" * 80)
        all_output.append("")

        for file_info in code_files:
            if (
                not include_large
                and file_info["error"]
                and "too large" in file_info["error"]
            ):
                continue

            formatted_output = format_file_for_ai(file_info, framework)
            all_output.append(formatted_output)
            all_output.append("-" * 80)
            all_output.append("")

    ouput_text = "\n".join(all_output)
    click.echo(ouput_text)
    if not no_copy and ouput_text:
        copy_to_clipboard(ouput_text, verbose=True)


if __name__ == "__main__":
    analyze_project()
