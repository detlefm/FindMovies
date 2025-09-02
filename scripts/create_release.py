import shutil
from pathlib import Path
import argparse

# --- Configuration ---
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIST_DIR = ROOT_DIR / "frontend" / "dist"

# --- Helper Functions ---
def rm_dir(path: Path):
    """Recursively removes a directory if it exists."""
    if path.is_dir():
        print(f"Removing existing directory: {path}")
        shutil.rmtree(path)

def copy(src: Path, dest: Path):
    """Copies a file."""
    print(f"Copying file: {src} -> {dest}")
    shutil.copy(src, dest)

def copy_tree(src: Path, dest: Path):
    """Copies a directory tree."""
    print(f"Copying directory: {src} -> {dest}")
    shutil.copytree(src, dest)

# --- Main Script ---
def main():
    """Assembles the release bundle."""
    parser = argparse.ArgumentParser(description="Create a release bundle for FindMovies.")
    parser.add_argument("destination", type=Path, help="The destination path to copy the release files to.")
    args = parser.parse_args()

    release_dir = args.destination
    print(f"--- Creating release bundle in: {release_dir} ---")

    # 1. Clean up old release directory
    if release_dir.exists():
        rm_dir(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    # 2. Create subdirectories
    (release_dir / "data").mkdir()
    (release_dir / "plugins").mkdir()
    (release_dir / "frontend").mkdir()

    # 3. Copy application files and directories
    print("\n--- Copying application files ---")
    copy_tree(BACKEND_DIR, release_dir / "backend")
    copy_tree(FRONTEND_DIST_DIR, release_dir / "frontend" / "dist")
    copy(ROOT_DIR / "app.yaml", release_dir / "app.yaml")
    copy(BACKEND_DIR / "requirements.txt", release_dir / "requirements.txt")
    copy(BACKEND_DIR / "env.example", release_dir / ".env.example")

    # 4. Copy README.md for the bundle
    print("\n--- Copying instruction file ---")
    copy(ROOT_DIR / "scripts" / "README.md", release_dir / "README.md")

    print("\n--- Release bundle created successfully! ---")
    print(f"Folder: {release_dir}")

if __name__ == "__main__":
    main()