from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web for recent information and give the accurate information.
    """
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
    except Exception as e:
        print(f"[web_search] Failed to load search tool: {e}")
        return "Error: Web search tool is currently unavailable due to missing system requirements."

    return search.run(query)