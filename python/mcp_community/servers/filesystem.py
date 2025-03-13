"""A FileSystem MCP server for local file system operations."""

from pathlib import Path
from typing import ClassVar

from mcp.server import FastMCP


class FileSystemMCPFactory:
    """Factory for creating FileSystem MCP servers with configurable options."""

    DEFAULT_ALLOWED_EXTENSIONS: ClassVar[list[str]] = [
        "txt",
        "md",
        "csv",
        "json",
        "yml",
        "yaml",
        "html",
    ]
    DEFAULT_MAX_FILE_SIZE: ClassVar[int] = 10 * 1024 * 1024  # 10MB default

    @classmethod
    def create(
        cls,
        base_directory: Path | str | None = None,
        allowed_extensions: list[str] | None = None,
        max_file_size: int | None = None,
        enable_read: bool = True,
        enable_write: bool = True,
        enable_list: bool = True,
        enable_create_dir: bool = True,
        enable_delete: bool = True,
    ) -> FastMCP:
        """Create a FileSystem MCP server with configurable options.

        Args:
            base_directory: Base directory for all file operations (default: current directory)
            allowed_extensions: List of allowed file extensions (default: DEFAULT_ALLOWED_EXTENSIONS)
            max_file_size: Maximum file size in bytes for read/write operations (default: DEFAULT_MAX_FILE_SIZE)
            enable_read: Enable the read_file tool (default: True)
            enable_write: Enable the write_file tool (default: True)
            enable_list: Enable the list_directory tool (default: True)
            enable_create_dir: Enable the create_directory tool (default: True)
            enable_delete: Enable the delete_file tool (default: True)

        Returns:
            FastMCP: Configured FileSystem MCP server
        """
        if base_directory is None:
            base_directory = Path.cwd()

        mcp = FastMCP("FileSystem")

        base_dir = Path(base_directory)
        allowed_exts = allowed_extensions or cls.DEFAULT_ALLOWED_EXTENSIONS
        file_size_limit = max_file_size or cls.DEFAULT_MAX_FILE_SIZE

        # Validation functions
        def _validate_path(path: str) -> str | None:
            """Validate path to prevent directory traversal."""
            file_path = base_dir / path

            try:
                if not file_path.resolve().is_relative_to(base_dir.resolve()):
                    return "Error: Path traversal attempt detected"
            except ValueError:
                # is_relative_to can raise ValueError on some Python versions
                return "Error: Invalid path"

            return None

        def _validate_extension(path: str) -> str | None:
            """Validate file extension."""
            extension = Path(path).suffix.lstrip(".")
            if extension not in allowed_exts:
                return f"Error: Invalid file extension. Allowed: {allowed_exts}"

            return None

        # Tool functions
        def read_file(path: str) -> str:
            """Read the contents of a file.

            Args:
                path: Path to the file, relative to the base directory

            Returns:
                str: Contents of the file or error message
            """
            try:
                if error := _validate_path(path):
                    return error

                if error := _validate_extension(path):
                    return error

                file_path = base_dir / path

                if not file_path.exists():
                    return f"Error: File {path} does not exist"

                if not file_path.is_file():
                    return f"Error: {path} is not a file"

                if file_path.stat().st_size > file_size_limit:
                    return (
                        f"Error: File exceeds maximum size of {file_size_limit} bytes"
                    )

                return file_path.read_text()
            except Exception as e:
                return f"Error reading file: {str(e)}"

        def write_file(path: str, content: str) -> str:
            """Write content to a file.

            Args:
                path: Path to the file, relative to the base directory
                content: Content to write to the file

            Returns:
                str: Success message or error message
            """
            try:
                if error := _validate_path(path):
                    return error

                if error := _validate_extension(path):
                    return error

                file_path = base_dir / path

                content_size = len(content.encode("utf-8"))
                if content_size > file_size_limit:
                    return f"Error: Content exceeds maximum size of {file_size_limit} bytes"

                # Create parent directories if they don't exist
                file_path.parent.mkdir(parents=True, exist_ok=True)

                file_path.write_text(content)
                return f"Successfully wrote to {path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        def list_directory(path: str = "") -> str:
            """List contents of a directory.

            Args:
                path: Path to directory, relative to the base directory. Default is base directory.

            Returns:
                str: Formatted directory listing or error message
            """
            try:
                if error := _validate_path(path):
                    return error

                dir_path = base_dir / path

                if not dir_path.exists():
                    return f"Error: Directory {path} does not exist"

                if not dir_path.is_dir():
                    return f"Error: {path} is not a directory"

                result = f"Contents of {path or '.'}:\n"
                for item in dir_path.iterdir():
                    item_type = "file" if item.is_file() else "directory"
                    size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                    result += f"- {item.name} [{item_type}]{size}\n"

                return result
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        def create_directory(path: str) -> str:
            """Create a directory.

            Args:
                path: Path to directory, relative to the base directory

            Returns:
                str: Success message or error message
            """
            try:
                if error := _validate_path(path):
                    return error

                dir_path = base_dir / path

                dir_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory {path}"
            except Exception as e:
                return f"Error creating directory: {str(e)}"

        def delete_file(path: str) -> str:
            """Delete a file.

            Args:
                path: Path to file, relative to the base directory

            Returns:
                str: Success message or error message
            """
            try:
                if error := _validate_path(path):
                    return error

                if error := _validate_extension(path):
                    return error

                file_path = base_dir / path

                if not file_path.exists():
                    return f"Error: File {path} does not exist"

                if not file_path.is_file():
                    return f"Error: {path} is not a file"

                file_path.unlink()
                return f"Successfully deleted {path}"
            except Exception as e:
                return f"Error deleting file: {str(e)}"

        # Register enabled tools
        if enable_read:
            mcp.tool()(read_file)

        if enable_write:
            mcp.tool()(write_file)

        if enable_list:
            mcp.tool()(list_directory)

        if enable_create_dir:
            mcp.tool()(create_directory)

        if enable_delete:
            mcp.tool()(delete_file)

        return mcp


mcp = FileSystemMCPFactory.create()
FileSystemMCP = mcp

__all__ = ["FileSystemMCP", "FileSystemMCPFactory"]


if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(FileSystemMCP)
