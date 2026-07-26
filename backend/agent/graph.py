from langgraph.graph import StateGraph, START
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from langgraph.prebuilt import tools_condition
from agent.tool_node import ThreadAwareToolNode

from agent.state import ChatState
from database.checkpointer import checkpointer
from tools.tool import tools

from typing import Annotated
from typing_extensions import TypedDict, NotRequired

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


load_dotenv()


# ============================================================
# MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
)

model = ChatHuggingFace(llm=llm)

title_llm = HuggingFaceEndpoint(
    repo_id="google/gemma-3-4b-it",     # Small model
    task="text-generation",
    temperature=0.9,                      
)

title_model = ChatHuggingFace(llm=title_llm)

import os

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)



# ============================================================
# BIND TOOLS
# ============================================================

llm_with_tools = model.bind_tools(tools)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI assistant with access to several tools.

Tool usage rules

1. Use the search tool whenever the user requests current, latest,
real-time or web information.

2. Use the stock tool whenever the user asks for a current stock price.

3. Use the calculator tool for mathematical calculations.

4. If the user asks questions about an uploaded PDF,
always use the rag_tool.

5. When calling rag_tool,
always include the current thread_id.

6. Never answer questions about uploaded documents
using your own knowledge.

7. After receiving the tool output,
use that context to answer naturally.
"""


# ============================================================
# CHAT NODE
# ============================================================

def chat_node(state: ChatState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    thread_id = state.get("thread_id")

    response = llm_with_tools.invoke(
        messages,
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    # Temporary debugging
    #print("\n========== MODEL DEBUG ==========")
    #print("CONTENT:", response.content)
    #print("TOOL CALLS:", response.tool_calls)
    #print("=================================\n")

    return {
        "messages": [response]
    }

    print("\n===== TOOL DEBUG =====")
    print("CONTENT:", response.content)
    print("TOOL CALLS:", response.tool_calls)
    print("======================\n")


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ThreadAwareToolNode(tools)

# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    graph = StateGraph(ChatState)

    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)

    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")

    return graph.compile(checkpointer=checkpointer)

chatbot = build_graph()