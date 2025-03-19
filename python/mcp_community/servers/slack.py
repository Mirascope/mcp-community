"""A Slack MCP server for basic Slack operations."""

import logging
import os
from typing import ClassVar

from mcp.server import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SlackMCP")


class SlackMCPFactory:
    """Factory for creating Slack MCP servers with configurable options."""

    DEFAULT_SLACK_API_TOKEN: ClassVar[str | None] = None

    @classmethod
    def create(
        cls,
        slack_token: str | None = DEFAULT_SLACK_API_TOKEN,
        log_level: str = "INFO",
    ) -> FastMCP:
        """Create a Slack MCP server with configurable options.

        Args:
            slack_token: Slack API token to authenticate (default: from SLACK_API_TOKEN environment variable)
            log_level: Logging level (default: "INFO")

        Returns:
            FastMCP: Configured Slack MCP server.
        """
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        if not slack_token:
            slack_token = os.environ.get("SLACK_API_TOKEN")
            if slack_token:
                logger.info("Slack API token found in environment variables")
            else:
                logger.error(
                    "No Slack API token provided. Please set SLACK_API_TOKEN environment variable."
                )
                raise ValueError("Slack API token is required.")

        # Create Slack client
        slack_client = WebClient(token=slack_token)

        # Create a new MCP server instance
        mcp = FastMCP("Slack")

        @mcp.tool()
        def post_message(channel: str, text: str) -> str:
            """Send a message to a Slack channel.

            Args:
                channel: The Slack channel ID or name (e.g., "#general" or "C12345678")
                text: The message text to send

            Returns:
                str: Success message or error message.
            """
            try:
                response = slack_client.chat_postMessage(channel=channel, text=text)
                if response["ok"]:
                    return f"Message sent to {channel}. Timestamp: {response['ts']}"
                else:
                    return f"Failed to send message: {response.get('error', 'Unknown error')}"
            except SlackApiError as e:
                logger.error(f"Slack API error: {e.response['error']}")
                return f"Slack API error: {e.response['error']}"
            except Exception as e:
                logger.error(f"Error posting message: {str(e)}")
                return f"Error posting message: {str(e)}"

        @mcp.tool()
        def get_channel_history(channel: str, limit: int = 10) -> str:
            """Retrieve the latest messages from a Slack channel.

            Args:
                channel: The Slack channel ID or name.
                limit: The maximum number of messages to retrieve (default: 10).

            Returns:
                str: Formatted channel history or error message.
            """
            try:
                response = slack_client.conversations_history(
                    channel=channel, limit=limit
                )
                if response["ok"]:
                    messages = response.get("messages", [])
                    result = f"Channel History for {channel}:\n\n"
                    for msg in messages:
                        user = msg.get("user", "Unknown")
                        text = msg.get("text", "")
                        ts = msg.get("ts", "")
                        result += f"User: {user}, Time: {ts}\nMessage: {text}\n\n"
                    return result
                else:
                    return f"Failed to retrieve channel history: {response.get('error', 'Unknown error')}"
            except SlackApiError as e:
                logger.error(f"Slack API error: {e.response['error']}")
                return f"Slack API error: {e.response['error']}"
            except Exception as e:
                logger.error(f"Error retrieving channel history: {str(e)}")
                return f"Error retrieving channel history: {str(e)}"

        @mcp.tool()
        def list_channels() -> str:
            """List all Slack channels in the workspace.

            Returns:
                str: Formatted list of channels or error message.
            """
            try:
                response = slack_client.conversations_list()
                if response["ok"]:
                    channels = response.get("channels", [])
                    result = "Channels:\n\n"
                    for channel in channels:
                        name = channel.get("name", "Unknown")
                        channel_id = channel.get("id", "Unknown")
                        result += f"Name: {name}, ID: {channel_id}\n"
                    return result
                else:
                    return f"Failed to list channels: {response.get('error', 'Unknown error')}"
            except SlackApiError as e:
                logger.error(f"Slack API error: {e.response['error']}")
                return f"Slack API error: {e.response['error']}"
            except Exception as e:
                logger.error(f"Error listing channels: {str(e)}")
                return f"Error listing channels: {str(e)}"

        logger.info("Slack MCP server created successfully")
        return mcp


# Create default instance with standard configuration
slack_mcp = SlackMCPFactory.create()
SlackMCP = slack_mcp

__all__ = ["SlackMCP", "SlackMCPFactory"]

if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(SlackMCP)
