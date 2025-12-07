import os
import click
from pathlib import Path


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
        ".ruff_cache"
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
        output.append("**Purpose:** [Brief description of what this file does]")
    else:
        output.append("*No content available*")

    return "\n".join(output)


@click.command()
@click.argument("path", required=False, default=os.getcwd())
@click.option(
    "--framework", "-f", help="Specify the framework (e.g., Fastapi, React, Django)"
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
def analyze_project(path, framework, max_size, output, include_large):
    """
    Analyze a project directory and return its structure with code content in AI-friendly format.

    PATH: Project directory path (default: current directory)
    """
    startpath = Path(path).resolve()

    if not startpath.exists():
        click.echo(f"Error: Path '{path}' does not exist")
        return

    if not startpath.is_dir():
        click.echo(f"Error: '{path}' is not a directory")
        return

    if output in ["structure", "both"]:
        click.echo("**Project Structure:**")
        click.echo(f"Path: {startpath}")
        click.echo()

        structure = get_directory_structure(startpath)
        for line in structure:
            click.echo(line)
        click.echo()

    if output in ["files", "both"]:
        code_files = get_code_files_with_content(startpath, max_file_size=max_size)

        if not code_files:
            click.echo("No code files found in the specified directory.")
            return

        click.echo("=" * 80)
        click.echo("CODE FILES IN AI-FRIENDLY FORMAT:")
        click.echo("=" * 80)
        click.echo()

        for file_info in code_files:
            if (
                not include_large
                and file_info["error"]
                and "too large" in file_info["error"]
            ):
                continue

            formatted_output = format_file_for_ai(file_info, framework)
            click.echo(formatted_output)
            click.echo("-" * 80)
            click.echo()


if __name__ == "__main__":
    analyze_project()
