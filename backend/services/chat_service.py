import uuid
from langchain_core.messages import AIMessage, HumanMessage
from agent.graph import llm_with_tools, title_model

from agent.graph import chatbot, model


def generate_thread_id() -> str:
    return str(uuid.uuid4())


def generate_chat_title(user_message: str) -> str:
    prompt = f"""
        Create the best short and clear title for this chat based on the user's first message.

        Rules:
        - Maximum 5 words
        - Return only the title
        - Do not use quotation marks
        - Do not use markdown
        - Do not add any explanation

        User message:
        {user_message}
        """
    response = title_model.invoke(prompt)

    title = response.content
    title = title.strip().strip('"').strip("'")

    print(f"GENERATED CHAT TITLE: {repr(title)}")
    if not title:
        title = "New Chat"

    return title



def make_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }


def load_conversation(thread_id: str) -> list[dict]:
    """Returns messages for a thread as plain dicts, ready for JSON."""
    state = chatbot.get_state(config=make_config(thread_id))
    messages = state.values.get("messages", [])

    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({
                "role": "user",
                "content": msg.content
                })

        elif isinstance(msg, AIMessage):
            # Ignore AI messages that only contain tool calls
            if msg.tool_calls and not msg.content:
                continue

            if msg.content:
                result.append({
                    "role": "assistant",
                    "content": msg.content
                })
    return result


def load_thread_name(thread_id: str) -> str:
    state = chatbot.get_state(config=make_config(thread_id))
    return state.values.get("chat_title", "New Chat")


def save_thread_title(thread_id: str, title: str) -> None:
    chatbot.update_state(make_config(thread_id), {"chat_title": title})


def stream_chat_response(
    thread_id: str,
    user_message: str,
):

    config = make_config(thread_id)
    response_started = False

    for message_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
        stream_mode="messages",
    ):

        # -------------------------------
        # Ignore non-AI messages
        # -------------------------------
        if not isinstance(message_chunk, AIMessage):
            continue

        # -------------------------------
        # Tool call started
        # -------------------------------
        if message_chunk.tool_calls:
            for tool_call in message_chunk.tool_calls:
                yield {
                    "type": "tool_start",
                    "tool": tool_call["name"],
                }

        # -------------------------------
        # Assistant text
        # -------------------------------
        content = message_chunk.content

        if not content:
            continue

        if not response_started:
            if not content.strip():
                continue

            content = content.lstrip()
            response_started = True

        yield {
            "type": "token",
            "content": content,
        }

    # -------------------------------
    # Tool finished
    # -------------------------------
    # (Temporary implementation)
    yield {
        "type": "tool_done",
        "tool": "",
    }