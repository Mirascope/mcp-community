"""A Google Calendar MCP server for calendar operations."""

import logging
import os
from typing import ClassVar

from mcp.server import FastMCP

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    HAS_GOOGLE_CALENDAR = True
except ImportError:
    HAS_GOOGLE_CALENDAR = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GoogleCalendarMCP")


class GoogleCalendarMCPFactory:
    """Factory for creating Google Calendar MCP servers with configurable options."""

    DEFAULT_CREDENTIALS_FILE: ClassVar[str | None] = None
    DEFAULT_SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/calendar"]

    @classmethod
    def create(
        cls,
        credentials_file: str | None = DEFAULT_CREDENTIALS_FILE,
        scopes: list[str] | None = None,
        log_level: str = "INFO",
    ) -> FastMCP:
        """Create a Google Calendar MCP server with configurable options.

        Args:
            credentials_file: Path to the service account credentials JSON file.
                              If not provided, the environment variable GOOGLE_CALENDAR_CREDENTIALS is used.
            scopes: List of OAuth scopes to use (default: ["https://www.googleapis.com/auth/calendar"]).
            log_level: Logging level (default: "INFO").

        Returns:
            FastMCP: Configured Google Calendar MCP server.
        """
        if not HAS_GOOGLE_CALENDAR:
            raise ImportError(
                "google-api-python-client and google-auth must be installed. "
                "Please install with `pip install google-api-python-client google-auth`."
            )

        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        if credentials_file is None:
            credentials_file = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS")
            if not credentials_file:
                raise ValueError(
                    "A credentials file must be provided or set in GOOGLE_CALENDAR_CREDENTIALS environment variable."
                )

        if scopes is None:
            scopes = cls.DEFAULT_SCOPES

        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=scopes
            )
            service = build("calendar", "v3", credentials=credentials)
        except Exception as e:
            raise RuntimeError(f"Error setting up Google Calendar service: {e}")

        # Create a new MCP server
        mcp = FastMCP("GoogleCalendar")

        @mcp.tool()
        def list_calendars() -> str:
            """List all calendars accessible by the service account."""
            try:
                calendar_list = service.calendarList().list().execute()
                items = calendar_list.get("items", [])
                if not items:
                    return "No calendars found."
                result = "Calendars:\n\n"
                for cal in items:
                    summary = cal.get("summary", "N/A")
                    cal_id = cal.get("id", "N/A")
                    result += f"Summary: {summary}, ID: {cal_id}\n"
                return result
            except Exception as e:
                logger.error(f"Error listing calendars: {e}")
                return f"Error listing calendars: {e}"

        @mcp.tool()
        def get_events(calendar_id: str, max_results: int = 10) -> str:
            """Retrieve events from a calendar.

            Args:
                calendar_id: The ID of the calendar.
                max_results: Maximum number of events to retrieve (default: 10).

            Returns:
                str: Formatted event list.
            """
            try:
                events_result = (
                    service.events()
                    .list(calendarId=calendar_id, maxResults=max_results)
                    .execute()
                )
                events = events_result.get("items", [])
                if not events:
                    return "No events found."
                result = f"Events for calendar {calendar_id}:\n\n"
                for event in events:
                    summary = event.get("summary", "No Title")
                    start = event.get("start", {}).get(
                        "dateTime", event.get("start", {}).get("date", "")
                    )
                    result += f"Title: {summary}, Start: {start}\n"
                return result
            except Exception as e:
                logger.error(f"Error retrieving events: {e}")
                return f"Error retrieving events: {e}"

        @mcp.tool()
        def create_event(
            calendar_id: str, summary: str, start_time: str, end_time: str
        ) -> str:
            """Create an event in a calendar.

            Args:
                calendar_id: The ID of the calendar.
                summary: Title of the event.
                start_time: Event start time in ISO format (e.g., '2025-04-01T10:00:00-07:00').
                end_time: Event end time in ISO format (e.g., '2025-04-01T11:00:00-07:00').

            Returns:
                str: Confirmation with event link.
            """
            try:
                event_body = {
                    "summary": summary,
                    "start": {"dateTime": start_time},
                    "end": {"dateTime": end_time},
                }
                event = (
                    service.events()
                    .insert(calendarId=calendar_id, body=event_body)
                    .execute()
                )
                link = event.get("htmlLink", "No link available")
                return f"Event created successfully: {link}"
            except Exception as e:
                logger.error(f"Error creating event: {e}")
                return f"Error creating event: {e}"

        @mcp.tool()
        def create_private_event(
            calendar_id: str, summary: str, start_time: str, end_time: str
        ) -> str:
            """Create a private event in a calendar.

            Args:
                calendar_id: The ID of the calendar.
                summary: Title of the event.
                start_time: Event start time in ISO format (e.g., '2025-04-01T10:00:00-07:00').
                end_time: Event end time in ISO format (e.g., '2025-04-01T11:00:00-07:00').

            Returns:
                str: Confirmation with event link.
            """
            try:
                event_body = {
                    "summary": summary,
                    "start": {"dateTime": start_time},
                    "end": {"dateTime": end_time},
                    "visibility": "private",  # Set the visibility to private
                }
                event = (
                    service.events()
                    .insert(calendarId=calendar_id, body=event_body)
                    .execute()
                )
                link = event.get("htmlLink", "No link available")
                return f"Private event created successfully: {link}"
            except Exception as e:
                logger.error(f"Error creating private event: {e}")
                return f"Error creating private event: {e}"

        logger.info("Google Calendar MCP server created successfully")
        return mcp


GoogleCalendarMCP = GoogleCalendarMCPFactory.create()

__all__ = ["GoogleCalendarMCP", "GoogleCalendarMCPFactory"]

if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(GoogleCalendarMCP)
