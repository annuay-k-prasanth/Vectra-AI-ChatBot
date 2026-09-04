import os
import requests

from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from typing import Optional

from services.rag_service import (
    rag_search,
    thread_has_document,
    thread_document_metadata,
)

load_dotenv()


# ============================================================
# SEARCH TOOL
# ============================================================

search_tool = DuckDuckGoSearchRun(
    region="us-en"
)


# ============================================================
# CALCULATOR TOOL
# ============================================================

@tool
def calculator(
    first_num: float,
    second_num: float,
    operation: str
) -> dict:
    """
    Perform basic arithmetic.

    Supported operations:
    - add
    - subtract
    - multiply
    - divide
    """

    try:

        if operation == "add":
            result = first_num + second_num

        elif operation == "subtract":
            result = first_num - second_num

        elif operation == "multiply":
            result = first_num * second_num

        elif operation == "divide":

            if second_num == 0:
                return {
                    "error": "Cannot divide by zero."
                }

            result = first_num / second_num

        else:
            return {
                "error": (
                    "Invalid operation. "
                    "Use add, subtract, multiply, or divide."
                )
            }

        return {
            "result": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# STOCK PRICE TOOL
# ============================================================

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Get the latest available stock quote for a stock symbol.

    Use this tool when the user asks for a current or latest stock price.
    """

    api_key = os.getenv("FINNHUB_API_KEY")

    response = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={
            "symbol": symbol.upper(),
            "token": api_key,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "symbol": symbol.upper(),
        "current_price": data.get("c"),
        "change": data.get("d"),
        "percent_change": data.get("dp"),
        "high": data.get("h"),
        "low": data.get("l"),
        "open": data.get("o"),
        "previous_close": data.get("pc"),
    }

# RAG tool

@tool
def rag_tool(
    query: str,
    thread_id: Optional[str] = None,
):
    """
    Search the uploaded PDF for relevant information.
    """
    if not thread_id:
        return {
            "error": "Missing thread_id."
        }

    has_document = thread_has_document(thread_id)
    print(f"RAG lookup: thread_id={thread_id}, has_document={has_document}")

    if not has_document:
        return {
            "error": "No PDF uploaded for this conversation."
        }

    result = rag_search(
        query=query,
        thread_id=thread_id,
        k=4,
    )

    result["document"] = thread_document_metadata(thread_id)

    return result


# ============================================================
# ALL AVAILABLE TOOLS
# ============================================================

tools = [
    search_tool,
    calculator,
    get_stock_price,
    rag_tool,
]

