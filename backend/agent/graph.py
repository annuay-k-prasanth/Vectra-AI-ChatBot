from langgraph.graph import StateGraph, START
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition

from agent.state import ChatState
from database.checkpointer import checkpointer
from tools.tool import tools


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
You are a helpful AI assistant with access to external tools.

Tool usage rules:

1. If the user asks for current, latest, or real-time information,
   use an appropriate available tool.

2. If the user asks for a current or latest stock price,
   always use the get_stock_price tool.

3. Never answer current stock-price questions from your internal knowledge.

4. Use the calculator tool for arithmetic calculations.

5. Use the search tool when current web information is required.

6. After receiving a tool result, use that result to answer the user clearly.
"""


# ============================================================
# CHAT NODE
# ============================================================

def chat_node(state: ChatState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

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

tool_node = ToolNode(tools)


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