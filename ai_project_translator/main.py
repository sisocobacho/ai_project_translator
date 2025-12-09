import os
import click
from pathlib import Path
import pyperclip
from typing import Set, Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

EXCLUDE_DIRS = ".git,__pycache__,node_modules,.vscode,.idea,venv,env,.venv,.ruff_cache,htmlcov,.pytest_cache"
EXTENSIONS = ".py,.js,.jsx,.ts,.tsx,.html,.css,.json,.xml,.yaml,.yml,.toml,.md,.txt"
MAX_SIZE = 600000
class Config(BaseSettings):
    """Configuration with environment variable support."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="AI_PT_",
        enable_decoding=False
    )

    # Core settings with environment variable support
    max_size: int = Field(
        default=MAX_SIZE,
        description="Maximum file size to read in bytes",
    )

    exclude_dirs: set[str] = Field(
        default=EXCLUDE_DIRS,
        description="Directories to exclude from analysis (comma-separated in env)",
    )


    extensions: set[str] = Field(
        default=EXTENSIONS,
        description="File extensions to include (comma-separated in env)",
    )
    
    
    extension_map: Dict[str, str] = Field(
        default={
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
        },
        description="Mapping of file extensions to language names",
    )

    max_depth: int = Field(
        default=3,
        description="Maximum depth for directory tree",
    )
    
    @field_validator('exclude_dirs', mode='before')
    @classmethod
    def decode_exclude_dirs(cls, v: str) -> set[str]:
        if not v.strip():
            v = EXCLUDE_DIRS
        return {x.strip() for x in v.split(',')}
    
    @field_validator('extensions', mode='before')
    @classmethod
    def decode_extensions(cls, v: str) -> set[str]:
        if not v.strip():
            v = EXTENSIONS
        return {x.strip() for x in v.split(',')}
    
    @field_validator('max_size', mode='before')
    @classmethod
    def decode_max_size(cls, v: str | int) -> int:
        if type(v) is int:
            return v
        if not v.strip():
            return MAX_SIZE
        return int(v)


# Global config instance
config = Config()

def format_question_for_output(question: Optional[str]) -> str:
    """Format the question for inclusion in the output."""
    if not question:
        return ""

    # Clean up the question - remove extra whitespace
    question = question.strip()

    # If question doesn't end with punctuation, add a period
    if question and question[-1] not in [".", "!", "?", ":"]:
        question = question + "."

    return question


def get_directory_structure(
    startpath: Path,
    exclude_dirs: Optional[set[str]] = None,
    max_depth: Optional[int] = None,
) -> list[str]:
    """
    Generate a tree-like structure of the directory
    """
    if exclude_dirs is None:
        exclude_dirs = config.exclude_dirs
    if max_depth is None:
        max_depth = config.max_depth

    structure = []

    def build_tree(path: Path, prefix: str = "", depth: int = 0):
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
            build_tree(path / directory, new_prefix, depth + 1)

        # Add files
        for i, file in enumerate(files):
            is_last = i == len(files) - 1
            connector = "└── " if is_last else "├── "
            structure.append(f"{prefix}{connector}{file}")

    structure.append(os.path.basename(startpath) + "/")
    build_tree(startpath)
    return structure


def get_file_extension_language(file_path: Path) -> str:
    """
    Map file extensions to language names for code blocks
    """
    extension_map = config.extension_map
    ext = file_path.suffix.lower()
    return extension_map.get(ext, "text")


def read_file_content(
    file_path: Path, max_size: Optional[int] = None
) -> tuple[Optional[str], Optional[str]]:
    """
    Read file content with size limitation
    """
    if max_size is None:
        max_size = config.max_size

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
    startpath: Path,
    extensions: Optional[Set[str]] = None,
    max_file_size: Optional[int] = None,
    exclude_dirs: Optional[Set[str]] = None,
) -> list[dict]:
    """
    Find all code files in the directory and read their content
    """
    if extensions is None:
        extensions = config.extensions
    if max_file_size is None:
        max_file_size = config.max_size
    if exclude_dirs is None:
        exclude_dirs = config.exclude_dirs

    code_files = []
    for root, dirs, files in os.walk(startpath):
        # Skip common excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = Path(root) / file
            if any(file.endswith(ext) for ext in extensions):
                relative_path = os.path.relpath(file_path, startpath)
                language = get_file_extension_language(file_path)
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


def get_single_file_info(
    file_path: Path, max_file_size: Optional[int] = None
) -> Optional[dict]:
    """
    Get information for a single file.
    """
    if max_file_size is None:
        max_file_size = config.max_size

    if not any(str(file_path).endswith(ext) for ext in config.extensions):
        return None

    relative_path = file_path.name
    language = get_file_extension_language(file_path)
    content, error = read_file_content(file_path, max_file_size)

    return {
        "path": relative_path,
        "full_path": file_path,
        "language": language,
        "content": content,
        "error": error,
        "size": file_path.stat().st_size if file_path.exists() else 0,
    }


def format_file_for_ai(file_info: dict, framework: Optional[str] = None) -> str:
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


def copy_to_clipboard(content: str, verbose: bool = True) -> bool:
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
    default=None,
    type=int,
    help="Maximum file size to read (bytes). Overrides AI_PT_MAX_SIZE env var.",
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
@click.option(
    "--show-config",
    is_flag=True,
    help="Show current configuration and exit",
)
def cli(
    path: str,
    framework: Optional[str],
    question: Optional[str],
    max_size: Optional[int],
    output: str,
    include_large: bool,
    no_copy: bool,
    show_config: bool,
):
    """
    Analyze a project directory and return its structure with code content in AI-friendly format.

    PATH: Project directory path or file path (default: current directory)

    If PATH is a file, only that file will be analyzed.
    If PATH is a directory, the entire directory will be analyzed.

    Configuration can be set via environment variables:
      - AI_PT_EXCLUDE_DIRS: Comma-separated list of directories to exclude
      - AI_PT_MAX_SIZE: Maximum file size in bytes
      - AI_PT_EXTENSIONS: Comma-separated list of file extensions to include
      - AI_PT_MAX_DEPTH: Maximum depth for directory tree
    """
    if show_config:
        click.echo("📋 Current Configuration:")
        click.echo(f"  Exclude directories: {', '.join(sorted(config.exclude_dirs))}")
        click.echo(f"  Max file size: {config.max_size} bytes")
        click.echo(f"  File extensions: {', '.join(sorted(config.extensions))}")
        click.echo(f"  Max directory depth: {config.max_depth}")
        click.echo("\nEnvironment variables used: AI_PT_*")
        click.echo(
            "Example: AI_PT_EXCLUDE_DIRS='dist,build,coverage' ai-pt /path/to/project"
        )
        return

    startpath = Path(path).resolve()

    if not startpath.exists():
        click.echo(f"Error: Path '{path}' does not exist")
        return

    # Use CLI max-size if provided, otherwise use config
    effective_max_size = max_size if max_size is not None else config.max_size

    # all what is going to be printed
    all_output = []

    # Add the question at the beginning if provided
    if question:
        formatted_question = format_question_for_output(question)
        all_output.append("**Question:**")
        all_output.append(f"{formatted_question}")
        all_output.append("")

    if startpath.is_file():
        # Single file analysis
        all_output.append("**Single File Analysis:**")
        all_output.append(f"File: {startpath.name}")
        all_output.append(f"Path: {startpath.parent}")
        all_output.append("")

        file_info = get_single_file_info(startpath, max_file_size=effective_max_size)

        if not file_info:
            click.echo(f"Error: '{startpath}' is not a supported code file type.")
            click.echo(f"Supported extensions: {', '.join(sorted(config.extensions))}")
            return

        all_output.append("=" * 80)
        all_output.append("FILE CONTENT:")
        all_output.append("=" * 80)
        all_output.append("")

        if (
            not include_large
            and file_info["error"]
            and "too large" in file_info["error"]
        ):
            click.echo(f"Skipping large file: {file_info['error']}")
            return

        formatted_output = format_file_for_ai(file_info, framework)
        all_output.append(formatted_output)

    else:
        # Directory analysis
        startpath_name = Path(path).name

        if output in ["structure", "both"]:
            all_output.append("**Project Structure:**")
            all_output.append(f"Path: {startpath_name}")
            all_output.append("")

            structure = get_directory_structure(startpath)
            all_output.extend(structure)
            all_output.append("")

        if output in ["files", "both"]:
            code_files = get_code_files_with_content(
                startpath, max_file_size=effective_max_size
            )

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
    cli()
