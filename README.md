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
uv pip install -e .
```
### Usage
```bash
ai-pt -q "Can you add logs to the project"
```
### Help
```bash
ai-pt --help   
```

## Developers
```bash
uv sync
```
### Usage
```bash
uv run main.py -q "Can you add logs to the project"
```
### Help
```bash
uv run main.py --help   
```
