from fastmcp import FastMCP
from rag import search_pdf as rag_search_pdf
import sys

mcp = FastMCP("My server")
@mcp.tool()
def search_pdf(query: str,filename: str) -> str:
    """Use this tool to find the answer from the pdf"""

    context = rag_search_pdf(query, filename)
    print(f"\n\nMCP CONTEXT {context} {type(context)}",file=sys.stderr)
    return context
if __name__ == "__main__":
    mcp.run()