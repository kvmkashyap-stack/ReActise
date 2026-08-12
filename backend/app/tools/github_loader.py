from pathlib import Path
import tempfile
import os
import shutil
import zipfile
import io
import httpx

from git import Repo
from langchain_core.documents import Document


def load_repository(
    repository_url: str,
    clone_to_dir: str = None,
) -> list[Document]:
    """
    Clone a GitHub repository and load source files.
    Uses git clone, falling back to zip archive download if git is unavailable.
    """
    temp_dir_ctx = None
    if clone_to_dir:
        if os.path.exists(clone_to_dir):
            shutil.rmtree(clone_to_dir, ignore_errors=True)
        os.makedirs(clone_to_dir, exist_ok=True)
        temp_dir = clone_to_dir
    else:
        temp_dir_ctx = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_ctx.name

    # Try Git Clone first
    try:
        Repo.clone_from(
            repository_url,
            temp_dir,
        )
    except Exception as git_err:
        print(f"[github_loader] git clone failed: {git_err}. Trying zip archive fallback...")
        # Clean up target directory content if git clone left half-cloned garbage
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        clean_url = repository_url.rstrip("/")
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]

        success = False
        # Try main branch, then master branch
        for branch in ["main", "master"]:
            zip_url = f"{clean_url}/archive/refs/heads/{branch}.zip"
            try:
                # Use httpx to fetch ZIP download
                response = httpx.get(zip_url, follow_redirects=True, timeout=30.0)
                if response.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        z.extractall(temp_dir)
                    
                    # Relocate files from the zip root subfolder (e.g. 'repo-name-main/') to temp_dir
                    subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if len(subdirs) == 1:
                        subfolder = os.path.join(temp_dir, subdirs[0])
                        for item in os.listdir(subfolder):
                            s_item = os.path.join(subfolder, item)
                            d_item = os.path.join(temp_dir, item)
                            if os.path.exists(d_item):
                                if os.path.isdir(d_item):
                                    shutil.rmtree(d_item)
                                else:
                                    os.remove(d_item)
                            shutil.move(s_item, d_item)
                        shutil.rmtree(subfolder)
                    success = True
                    break
            except Exception as zip_err:
                print(f"[github_loader] ZIP fallback failed for {branch}: {zip_err}")

        if not success:
            if temp_dir_ctx:
                temp_dir_ctx.cleanup()
            raise ValueError(f"Could not clone or index repository. Git error: {git_err}")

    documents = []

    for file in Path(temp_dir).rglob("*"):
        if any(part.startswith('.') for part in file.parts) or "node_modules" in file.parts:
            continue

        if file.is_file() and file.suffix in {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".md",
            ".json",
            ".html",
            ".css",
        }:
            try:
                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                rel_path = file.relative_to(temp_dir)

                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "path": str(rel_path),
                        },
                    )
                )
            except Exception:
                continue

    if not clone_to_dir and temp_dir_ctx:
        temp_dir_ctx.cleanup()

    return documents