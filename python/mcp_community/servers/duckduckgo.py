"""A simple calculator MCP server."""

import inspect
import re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage

mcp = FastMCP("DuckDuckGoMCP")


@mcp.tool()
def text_search(query: str, max_results: int = 5) -> str:
    """Returns the results of a text web search query.

    Args:
        query (str): The search query
        max_results (int): The maximum number of search results to return (default: 5)

    Returns:
        str: Formatted search results if successful, error message if search fails
    """

    try:
        results = DDGS().text(keywords=query, max_results=max_results)
        return "\n\n".join(
            inspect.cleandoc(
                f"""
                Title: {result.get('title', 'N/A')}
                URL: {result.get('href', 'N/A')}
                Snippet: {result.get('body', 'N/A')}
                """
            )
            for result in results
        )
    except Exception as e:
        return f"{type(e).__name__}: {str(e)} - Failed to search the web for text"


@mcp.tool()
def news_search(query: str, max_results: int = 5) -> str:
    """Returns the results of a news web search query.

    Args:
        query (str): The search query
        max_results (int): The maximum number of search results to return (default: 5)

    Returns:
        str: Formatted search results if successful, error message if search fails
    """
    try:
        results = DDGS().news(query, max_results=max_results)
        return "\n\n".join(
            inspect.cleandoc(
                f"""
                Date: {result.get('date', 'N/A')}
                Title: {result.get('title', 'N/A')}
                URL: {result.get('url', 'N/A')}
                Image: {result.get('image', 'N/A')}
                Source: {result.get('source', 'N/A')}
                Snippet: {result.get('body', 'N/A')}\
                """
            )
            for result in results
        )
    except Exception as e:
        return f"{type(e).__name__}: {str(e)} - Failed to search the web for news"


@mcp.tool()
def image_search(
    query: str,
    size: str | None = None,
    color: str | None = None,
    type_image: str | None = None,
    layout: str | None = None,
    license_image: str | None = None,
    max_results: int = 5,
) -> str:
    """Returns the results of an image web search query."""
    try:
        results = DDGS().images(
            keywords=query,
            size=size,
            color=color,
            type_image=type_image,
            layout=layout,
            license_image=license_image,
            max_results=max_results,
        )
        return "\n\n".join(
            inspect.cleandoc(
                f"""
                Title: {result.get('title', 'N/A')}
                Image: {result.get('image', 'N/A')}
                URL: {result.get('url', 'N/A')}
                Height: {result.get('height', 'N/A')}
                Width: {result.get('width', 'N/A')}
                Source: {result.get('source', 'N/A')}
                Thumbnail: {result.get('thumbnail', 'N/A')}
                """
            )
            for result in results
        )

    except Exception as e:
        return f"{type(e).__name__}: {str(e)} - Failed to search the web for images"


@mcp.tool()
def parse_url_content(url: str) -> str:
    """Returns the cleaned text content from a URL if successful, error message on failure."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        unwanted_tags = ["script", "style", "nav", "header", "footer", "aside"]
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile("content|main"))
        )
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        lines = (line.strip() for line in text.splitlines())
        content = "\n".join(line for line in lines if line)
        if not content:
            return "No content found on the page"
        return content
    except requests.RequestException as e:
        return f"Failed to fetch content from URL: {str(e)}"
    except Exception as e:
        return f"{type(e).__name__}: Failed to parse content from URL"


@mcp.tool()
def load_image_from_url(url: str, width: int = 100, height: int = 100) -> Image:
    response = requests.get(url)
    image_path = BytesIO(response.content)
    img = PILImage.open(image_path)
    img.thumbnail((width, height))
    return Image(path=url, data=img.tobytes())


DuckDuckGoMCP = mcp

__all__ = ["DuckDuckGoMCP"]


if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(DuckDuckGoMCP)
