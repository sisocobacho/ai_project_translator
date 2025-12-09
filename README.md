# AI Project Translator

A tool to analyze project directories and returns it structure and code for AI context. After the analysis it automatically copy the result to the clipboard then You can copy to your favorite ai chat. Hopely it gives better context and achives better results.

## Features

- Project Structure Analysis: Generates clean tree structure of directories

- Code File Extraction: Reads and formats code files for AI context

- Single File Support: Can analyze individual files

- Question Support: Include your question at the beginning of output

- Framework Specification: Specify project framework for context

- Clipboard Integration: Output automatically copied to clipboard

- Configurable: Control file size limits, output format, and exclusions

## Installation

```bash
git clone https://github.com/sisocobacho/ai_project_translator.git
cd ai_project_translator    
uv pip install -e .
```
### Usage
```bash
ai-pt path/project -q "Can you add logs to the project"
```
#### Help
```bash
ai-pt --help   
```
Shows all options available
```bash
Options:
  -f, --framework TEXT            Specify the framework (e.g., Fastapi, React,
                                  Django)
  -q, --question TEXT             Include a question to ask the AI at the
                                  beginning of the output
  -m, --max-size INTEGER          Maximum file size to read (bytes). Overrides
                                  AI_PT_MAX_SIZE env var.
  -o, --output [structure|files|both]
                                  Output format
  -l, --include-large             Include large files (content will be
                                  skipped)
  --no-copy                       Do not copy to clipboard (print only)
  --show-config                   Show current configuration and exit
  --exclude-files TEXT            Exclude files from analisys
  --help                          Show this message and exit.
```

#### Configuration 
You can see the current configuration using the show-config option. 
It will output the current configuration values.

```bash
ai-pt --show-config   
```
Configuration can be set via environment variables:
 - AI_PT_EXCLUDE_DIRS: Comma-separated list of directories to exclude
 - AI_PT_EXCLUDE_FILES: Comma-separated list of files to exclude
 - AI_PT_MAX_SIZE: Maximum file size in bytes
 - AI_PT_EXTENSIONS: Comma-separated list of file extensions to include
 - AI_PT_MAX_DEPTH: Maximum depth for directory tree

For example:

```bash
export AI_PT_EXCLUDE_DIRS='dist,build,coverage' 
ai-pt --show-config   
```
To go back to defaults

```bash
unset AI_PT_EXCLUDE_DIRS='dist,build,coverage' 
ai-pt --show-config   
```

## Developers
```bash
git clone https://github.com/sisocobacho/ai_project_translator.git
cd ai_project_translator    
uv sync
```
### Usage
```bash
uv run ai_project_translator/main.py path/project -q "Can you add logs to the project"
```
