"""Project Workspace Manager - Manages folders and files for each venture/product."""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """
    Manages project workspaces with file/folder structure for each venture.
    Each venture gets its own isolated workspace with organized folders.
    """

    def __init__(self, base_path: str = "agent_data/workspaces"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_workspace(
        self,
        venture_id: int,
        venture_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new workspace for a venture/product.

        Args:
            venture_id: Venture/opportunity ID
            venture_name: Name of the venture
            metadata: Additional metadata

        Returns:
            Path to workspace
        """
        # Sanitize name for folder
        safe_name = self._sanitize_name(venture_name)
        workspace_name = f"venture_{venture_id}_{safe_name}"
        workspace_path = self.base_path / workspace_name

        # Create workspace structure
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Standard folders
        folders = [
            "code",          # Source code
            "docs",          # Documentation
            "data",          # Data files
            "config",        # Configuration
            "output",        # Generated outputs
            "logs",          # Logs specific to this venture
            "assets",        # Images, media, etc.
            "tests",         # Test files
            "deploy",        # Deployment artifacts
            "research"       # Research and analysis
        ]

        for folder in folders:
            (workspace_path / folder).mkdir(exist_ok=True)

        # Create workspace manifest
        manifest = {
            "venture_id": venture_id,
            "venture_name": venture_name,
            "created_at": datetime.utcnow().isoformat(),
            "workspace_path": str(workspace_path),
            "metadata": metadata or {},
            "structure": folders
        }

        self._save_manifest(workspace_path, manifest)

        # Create README
        readme_content = f"""# {venture_name}

**Venture ID:** {venture_id}
**Created:** {manifest['created_at']}

## Workspace Structure

- `code/` - Source code and scripts
- `docs/` - Documentation and guides
- `data/` - Data files and datasets
- `config/` - Configuration files
- `output/` - Generated outputs and results
- `logs/` - Venture-specific logs
- `assets/` - Media and static files
- `tests/` - Test files and test data
- `deploy/` - Deployment artifacts
- `research/` - Research and analysis documents

## Status

See `workspace.json` for current status and metadata.
"""

        self.write_file(workspace_path, "README.md", readme_content)

        logger.info(f"Created workspace: {workspace_path}")
        return str(workspace_path)

    def get_workspace_path(self, venture_id: int) -> Optional[Path]:
        """Get workspace path for a venture."""
        # Find workspace by ID
        for workspace in self.base_path.iterdir():
            if workspace.is_dir() and workspace.name.startswith(f"venture_{venture_id}_"):
                return workspace
        return None

    def write_file(
        self,
        workspace_path: Path,
        relative_path: str,
        content: str,
        mode: str = "w"
    ) -> str:
        """
        Write a file in the workspace.

        Args:
            workspace_path: Workspace path
            relative_path: Relative path within workspace
            content: File content
            mode: Write mode ('w' or 'a')

        Returns:
            Full file path
        """
        file_path = Path(workspace_path) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Wrote file: {file_path}")
        return str(file_path)

    def read_file(self, workspace_path: Path, relative_path: str) -> Optional[str]:
        """Read a file from workspace."""
        file_path = Path(workspace_path) / relative_path

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def list_files(
        self,
        workspace_path: Path,
        folder: Optional[str] = None,
        pattern: str = "*"
    ) -> List[str]:
        """
        List files in workspace or specific folder.

        Args:
            workspace_path: Workspace path
            folder: Optional subfolder
            pattern: Glob pattern

        Returns:
            List of relative file paths
        """
        search_path = Path(workspace_path)
        if folder:
            search_path = search_path / folder

        if not search_path.exists():
            return []

        files = []
        for file_path in search_path.rglob(pattern):
            if file_path.is_file():
                relative = file_path.relative_to(workspace_path)
                files.append(str(relative))

        return files

    def delete_workspace(self, venture_id: int) -> bool:
        """
        Delete a workspace.

        Args:
            venture_id: Venture ID

        Returns:
            True if deleted, False if not found
        """
        workspace_path = self.get_workspace_path(venture_id)
        if not workspace_path:
            logger.warning(f"Workspace not found for venture {venture_id}")
            return False

        try:
            shutil.rmtree(workspace_path)
            logger.info(f"Deleted workspace: {workspace_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting workspace: {e}")
            return False

    def archive_workspace(self, venture_id: int) -> Optional[str]:
        """
        Archive a workspace (zip it and mark as archived).

        Args:
            venture_id: Venture ID

        Returns:
            Path to archive file or None
        """
        workspace_path = self.get_workspace_path(venture_id)
        if not workspace_path:
            return None

        archive_dir = self.base_path / "archives"
        archive_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{workspace_path.name}_{timestamp}"
        archive_path = archive_dir / archive_name

        try:
            shutil.make_archive(str(archive_path), 'zip', workspace_path)
            logger.info(f"Archived workspace to: {archive_path}.zip")
            return f"{archive_path}.zip"
        except Exception as e:
            logger.error(f"Error archiving workspace: {e}")
            return None

    def update_workspace_status(
        self,
        venture_id: int,
        status: str,
        notes: Optional[str] = None
    ):
        """Update workspace status."""
        workspace_path = self.get_workspace_path(venture_id)
        if not workspace_path:
            return

        manifest = self._load_manifest(workspace_path)
        if manifest:
            manifest["status"] = status
            manifest["updated_at"] = datetime.utcnow().isoformat()
            if notes:
                manifest["notes"] = notes
            self._save_manifest(workspace_path, manifest)

    def get_workspace_info(self, venture_id: int) -> Optional[Dict[str, Any]]:
        """Get workspace information."""
        workspace_path = self.get_workspace_path(venture_id)
        if not workspace_path:
            return None

        manifest = self._load_manifest(workspace_path)

        # Calculate workspace size
        total_size = sum(
            f.stat().st_size
            for f in workspace_path.rglob('*')
            if f.is_file()
        )

        # Count files
        file_count = sum(1 for _ in workspace_path.rglob('*') if _.is_file())

        info = manifest or {}
        info.update({
            "path": str(workspace_path),
            "size_bytes": total_size,
            "file_count": file_count,
            "exists": workspace_path.exists()
        })

        return info

    def list_all_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces."""
        workspaces = []

        for workspace_path in self.base_path.iterdir():
            if workspace_path.is_dir() and workspace_path.name.startswith("venture_"):
                manifest = self._load_manifest(workspace_path)
                if manifest:
                    manifest["path"] = str(workspace_path)
                    workspaces.append(manifest)

        return workspaces

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in folder names."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')

        # Limit length
        name = name[:50]

        # Remove leading/trailing spaces and dots
        name = name.strip('. ')

        # Replace spaces with underscores
        name = name.replace(' ', '_')

        return name.lower()

    def _save_manifest(self, workspace_path: Path, manifest: Dict[str, Any]):
        """Save workspace manifest."""
        manifest_path = workspace_path / "workspace.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

    def _load_manifest(self, workspace_path: Path) -> Optional[Dict[str, Any]]:
        """Load workspace manifest."""
        manifest_path = workspace_path / "workspace.json"
        if not manifest_path.exists():
            return None

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return None
