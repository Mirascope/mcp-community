"""A Docker Sandbox MCP server for safely executing code in containers."""

import io
import logging
import tarfile
import time
from typing import ClassVar

import docker
from docker import DockerClient
from docker.errors import APIError, ContainerError, DockerException
from mcp.server import FastMCP

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DockerSandbox")


class DockerSandboxMCPFactory:
    """Factory for creating Docker Sandbox MCP servers with configurable options."""

    # Default settings
    DEFAULT_PYTHON_IMAGE: ClassVar[str] = "python:3.12-slim"
    DEFAULT_ALPINE_IMAGE: ClassVar[str] = "alpine:latest"
    DEFAULT_MEMORY_LIMIT: ClassVar[str] = "512m"
    DEFAULT_CPU_LIMIT: ClassVar[float] = 1.0
    DEFAULT_TIMEOUT: ClassVar[int] = 30  # seconds
    DEFAULT_COMMAND_TIMEOUT: ClassVar[int] = 25  # seconds for individual commands
    DEFAULT_NETWORK_ACCESS: ClassVar[bool] = False
    DEFAULT_MAX_OUTPUT_SIZE: ClassVar[int] = 10 * 1024  # 10KB
    DEFAULT_OUTPUT_ENCODING: ClassVar[str] = "utf-8"
    DEFAULT_NON_ROOT_USER: ClassVar[bool] = True

    @classmethod
    def create(
        cls,
        python_image: str = DEFAULT_PYTHON_IMAGE,
        alpine_image: str = DEFAULT_ALPINE_IMAGE,
        memory_limit: str = DEFAULT_MEMORY_LIMIT,
        cpu_limit: float = DEFAULT_CPU_LIMIT,
        timeout: int = DEFAULT_TIMEOUT,
        command_timeout: int = DEFAULT_COMMAND_TIMEOUT,
        network_access: bool = DEFAULT_NETWORK_ACCESS,
        max_output_size: int = DEFAULT_MAX_OUTPUT_SIZE,
        output_encoding: str = DEFAULT_OUTPUT_ENCODING,
        enable_python: bool = True,
        enable_bash: bool = True,
        use_non_root_user: bool = DEFAULT_NON_ROOT_USER,
        log_level: str = "INFO",
    ) -> FastMCP:
        """Create a Docker Sandbox MCP server with configurable options."""
        logger.setLevel(getattr(logging, log_level))

        mcp = FastMCP("DockerSandbox")

        try:
            docker_client = docker.from_env()
            docker_client.ping()
            logger.info("Successfully connected to Docker daemon")
        except DockerException as e:
            logger.error(f"Failed to connect to Docker daemon: {str(e)}")
            raise RuntimeError(f"Failed to connect to Docker daemon: {str(e)}")

        cls._pull_images(docker_client, [python_image, alpine_image])

        execution_config = {
            "memory_limit": memory_limit,
            "cpu_limit": cpu_limit,
            "timeout": timeout,
            "command_timeout": command_timeout,
            "network_access": network_access,
            "max_output_size": max_output_size,
            "output_encoding": output_encoding,
            "use_non_root_user": use_non_root_user,
        }

        def execute_python(code: str, requirements: list[str] | None = None) -> str:
            """Execute Python code in a sandboxed Docker container."""
            files = {"main.py": code}

            if requirements and not network_access:
                logger.warning(
                    "Package installation requested but network access is disabled"
                )
                return "Error: Cannot install requirements without network access"

            if requirements and network_access:
                logger.info(f"Adding requirements: {', '.join(requirements)}")
                files["requirements.txt"] = "\n".join(requirements)

            commands = []
            if requirements and network_access:
                commands.append("pip install --no-cache-dir -r requirements.txt")
            commands.append("python main.py")

            return cls._execute_in_container(
                docker_client=docker_client,
                image=python_image,
                files=files,
                commands=commands,
                **execution_config,
            )

        def execute_bash(commands: str) -> str:
            """Execute bash commands in a sandboxed Docker container."""
            return cls._execute_in_container(
                docker_client=docker_client,
                image=alpine_image,
                files={"script.sh": commands},
                commands=["chmod +x script.sh", "./script.sh"],
                **execution_config,
            )

        if enable_python:
            logger.info("Registering Python execution tool")
            mcp.tool()(execute_python)

        if enable_bash:
            logger.info("Registering Bash execution tool")
            mcp.tool()(execute_bash)

        logger.info(
            f"DockerSandbox MCP server created successfully with: "
            f"memory_limit={memory_limit}, cpu_limit={cpu_limit}, "
            f"network_access={network_access}"
        )
        return mcp

    @staticmethod
    def _pull_images(docker_client: DockerClient, images: list[str]) -> None:
        for image in images:
            try:
                logger.info(f"Pulling Docker image: {image}")
                docker_client.images.pull(image)
                logger.info(f"Successfully pulled image: {image}")
            except DockerException as e:
                logger.warning(f"Failed to pull image {image}: {str(e)}")

    @staticmethod
    def _create_tar_stream(files: dict[str, str]) -> io.BytesIO:
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as tar:
            for name, content in files.items():
                info = tarfile.TarInfo(name=name)
                encoded_content = content.encode("utf-8")
                info.size = len(encoded_content)
                tar.addfile(info, io.BytesIO(encoded_content))
        stream.seek(0)
        return stream

    @staticmethod
    def _truncate_output(output: str, max_size: int) -> str:
        if len(output.encode("utf-8")) > max_size:
            truncated = output.encode("utf-8")[:max_size].decode(
                "utf-8", errors="ignore"
            )
            return f"{truncated}\n... Output truncated (exceeded {max_size} bytes)"
        return output

    @classmethod
    def _execute_in_container(
        cls,
        docker_client: DockerClient,
        image: str,
        files: dict[str, str],
        commands: list[str],
        memory_limit: str,
        cpu_limit: float,
        timeout: int,
        command_timeout: int,
        network_access: bool,
        max_output_size: int,
        output_encoding: str,
        use_non_root_user: bool,
    ) -> str:
        container = None
        execution_start_time = time.time()

        try:
            user = "root"
            if use_non_root_user:
                if "python" in image:
                    user = "1000"
                elif "alpine" in image:
                    user = "root"

            logger.info(
                f"Creating container with image {image}, "
                f"network_access={network_access}, memory_limit={memory_limit}"
            )

            container = docker_client.containers.run(
                image=image,
                command=["sleep", str(timeout)],
                detach=True,
                user=user if user != "root" else None,
                mem_limit=memory_limit,
                nano_cpus=int(cpu_limit * 1e9),
                network_disabled=not network_access,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
                remove=True,
            )

            logger.info(f"Copying {len(files)} files to container")
            tar_stream = cls._create_tar_stream(files)
            container.put_archive("/", tar_stream)

            full_output = []
            exit_codes = []

            for i, command in enumerate(commands):
                if time.time() - execution_start_time > timeout:
                    logger.warning(f"Overall timeout reached after {i} commands")
                    full_output.append(f"Operation timed out after {timeout} seconds")
                    break

                remaining_time = min(
                    command_timeout, timeout - int(time.time() - execution_start_time)
                )

                if remaining_time <= 0:
                    logger.warning("No time remaining for command execution")
                    full_output.append("Operation timed out")
                    break

                logger.info(f"Executing command: {command}")
                try:
                    exec_result = container.exec_run(
                        cmd=["sh", "-c", command], demux=True
                    )

                    exit_codes.append(exec_result.exit_code)

                    stdout = (
                        exec_result.output[0].decode(output_encoding, errors="replace")
                        if exec_result.output[0]
                        else ""
                    )
                    stderr = (
                        exec_result.output[1].decode(output_encoding, errors="replace")
                        if exec_result.output[1]
                        else ""
                    )

                    if stdout:
                        full_output.append(stdout)
                    if stderr:
                        full_output.append(f"Error: {stderr}")

                    if exec_result.exit_code != 0:
                        error_msg = "Unknown error"
                        if exec_result.exit_code == 127:
                            error_msg = "Command not found"
                        elif exec_result.exit_code == 126:
                            error_msg = "Permission denied"
                        elif exec_result.exit_code == 124:
                            error_msg = "Command timed out"

                        logger.warning(
                            f"Command failed: {command} (Exit code: {exec_result.exit_code}, {error_msg})"
                        )
                        full_output.append(
                            f"Command failed: {error_msg} (Exit code: {exec_result.exit_code})"
                        )
                        break

                except Exception as e:
                    logger.error(f"Error executing command '{command}': {str(e)}")
                    full_output.append(f"Error executing command: {str(e)}")
                    break

            output = "\n".join(full_output)
            return cls._truncate_output(output, max_output_size)

        except ContainerError as e:
            logger.error(f"Container error: {str(e)}")
            return f"Container error: {str(e)}"
        except APIError as e:
            logger.error(f"Docker API error: {str(e)}")
            return f"Docker API error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"
        finally:
            if container:
                try:
                    logger.info("Stopping and removing container")
                    container.stop(timeout=1)
                except Exception as e:
                    logger.warning(f"Error while stopping container: {str(e)}")


# Default instance with standard configuration
mcp = DockerSandboxMCPFactory.create()
DockerSandboxMCP = mcp

__all__ = ["DockerSandboxMCP", "DockerSandboxMCPFactory"]


if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(DockerSandboxMCP)
