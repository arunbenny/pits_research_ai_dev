import time

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults


search_engine = DuckDuckGoSearchResults(
    output_format="list",
    max_results=5,
)


@tool
def search_web(query: str) -> list:
    """
    Search the web and return structured search results
    containing titles, URLs, and snippets.
    """

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:

            print(
                f"Web search attempt "
                f"{attempt}/{max_retries}: {query}"
            )

            results = search_engine.invoke(query)

            if results:
                return results

        except Exception as error:

            print(
                f"Web search attempt {attempt} failed: "
                f"{error}"
            )

            if attempt < max_retries:
                time.sleep(2)

    return []