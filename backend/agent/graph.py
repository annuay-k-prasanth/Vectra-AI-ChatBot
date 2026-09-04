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
from services.rag_service import thread_document_metadata, thread_has_document

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
    model="openai/gpt-oss-20b",
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
You are Vectra AI, an AI assistant with access to several tools.

User conversation preferences

- Adapt to the user's stated preferences for the conversation, including the
  names to use for the user and assistant, tone, style, and context, as long
  as they are safe.
- Apply these preferences naturally throughout the current conversation. For
  example, if a user says to call them Vijay and to use the name Surya for the
  assistant, address them as Vijay and refer to yourself as Surya.
- Use Vectra AI as your default name only when the user has not given a
  different name or conversation preference.
- If the user asks who you are after assigning you a name, answer using their
  assigned name, not Vectra AI. For example: "I'm Surya, Vijay."

Identity rules

- Do not describe yourself as the underlying LLM or reveal the model name
  unless the user explicitly asks about the technical model powering Vectra AI.

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

Document-review response style

When reviewing a resume or another uploaded document, write for a person who
wants useful, quick feedback:
- Start with one short, encouraging overall impression.
- Use the headings "Top improvements" and "What to do next".
- Under "Top improvements", give at most five numbered, high-impact items.
  For each: name the section, say what you noticed, then give a concrete fix.
- Under "What to do next", give three short actions in priority order.
- Use plain text headings, numbers, and short lines. Do not use Markdown
  tables, pipes, or long audit-style columns; the chat UI displays plain text.
- Base every observation on the retrieved document. Do not invent metrics,
  missing sections, spelling errors, or details that are not in the PDF.
- Keep the answer concise unless the user asks for a detailed review.
"""


# ============================================================
# CHAT NODE
# ============================================================

def chat_node(state: ChatState):

    thread_id = state.get("thread_id")
    document_context = ""

    if thread_id and thread_has_document(thread_id):
        document = thread_document_metadata(thread_id)
        filename = document.get("filename", "the uploaded PDF")
        document_context = f"""

An uploaded PDF is already indexed for this conversation: {filename}.
Do not ask the user to upload it again. Treat references to the document,
PDF, attachment, resume, or its contents as requests about this indexed file,
and call rag_tool before answering.
"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT + document_context),
        *state["messages"],
    ]

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
