import os
import ast
import json
from langchain_core.tools import tool


@tool
def list_workspace_files(
    user_id: str,
    repo_name: str,
) -> list[str]:
    """
    List all file paths available in the cloned repository workspace.
    Use this to see the structure of the repository.
    """
    workspace_dir = os.path.join("workspaces", user_id, repo_name)
    if not os.path.exists(workspace_dir):
        return [f"Workspace for repo '{repo_name}' not found."]

    file_list = []
    for root, dirs, files in os.walk(workspace_dir):
        # Exclude hidden directories, node_modules, and cache files
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != "node_modules" and d != "__pycache__"]
        for file in files:
            if file.startswith('.'):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, workspace_dir)
            file_list.append(rel_path)

    return file_list


@tool
def read_workspace_file(
    user_id: str,
    repo_name: str,
    file_path: str,
) -> str:
    """
    Read the complete text content of a specific file from the repository workspace.
    Use this to inspect code, analyze files, and find bugs.
    """
    safe_path = os.path.normpath(file_path).lstrip("/\\")
    full_path = os.path.join("workspaces", user_id, repo_name, safe_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return f"File '{file_path}' not found in workspace."

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_workspace_file(
    user_id: str,
    repo_name: str,
    file_path: str,
    content: str,
) -> str:
    """
    Write or overwrite a file in the workspace directory with new content.
    Use this to save code corrections, write fixes, or create new files.
    """
    safe_path = os.path.normpath(file_path).lstrip("/\\")
    full_path = os.path.join("workspaces", user_id, repo_name, safe_path)

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote file to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def check_code_syntax(
    user_id: str,
    repo_name: str,
    file_path: str,
) -> str:
    """
    Check the syntax and compile stability of a file in the workspace.
    Supports python (.py) syntax validation and JSON validation.
    Use this to verify if code corrections are free of syntax errors.
    """
    safe_path = os.path.normpath(file_path).lstrip("/\\")
    full_path = os.path.join("workspaces", user_id, repo_name, safe_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return f"File '{file_path}' not found in workspace."

    ext = os.path.splitext(full_path)[1].lower()

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            file_content = f.read()

        if ext == ".py":
            ast.parse(file_content)
            return "Syntax Check: Python syntax is valid (ast.parse passed)."
        elif ext == ".json":
            json.loads(file_content)
            return "Syntax Check: JSON format is valid."
        else:
            return f"Syntax Check: File format '{ext}' is not supported for syntax parsing. Checked readability only."
    except SyntaxError as se:
        return f"Syntax Error in '{file_path}': line {se.lineno}, col {se.offset}: {se.msg}\nCode line: {se.text}"
    except json.JSONDecodeError as jde:
        return f"JSON Format Error in '{file_path}': line {jde.lineno}, col {jde.colno}: {jde.msg}"
    except Exception as e:
        return f"Validation Error in '{file_path}': {str(e)}"
