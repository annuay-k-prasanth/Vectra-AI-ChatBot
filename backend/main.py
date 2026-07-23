import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database.checkpointer import retrieve_all_threads, delete_thread
from services.chat_service import (
    generate_thread_id,
    generate_chat_title,
    load_conversation,
    load_thread_name,
    save_thread_title,
    stream_chat_response,
)

app = FastAPI(title="Chatbot API")

# Allow the React dev server to call this API.
# Tighten allow_origins to your real frontend domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str
    message: str


@app.post("/threads")
def create_thread():
    """Create a new, empty conversation thread."""
    thread_id = generate_thread_id()
    return {"thread_id": thread_id, "title": "New Chat"}


@app.get("/threads")
def list_threads():
    """List all threads with their saved titles, most recent first."""
    thread_ids = retrieve_all_threads()
    threads = [
        {"thread_id": tid, "title": load_thread_name(tid)}
        for tid in thread_ids
    ]
    return {"threads": threads}


@app.get("/threads/{thread_id}/messages")
def get_thread_messages(thread_id: str):
    """Return the full message history for a thread."""
    return {"thread_id": thread_id, "messages": load_conversation(thread_id)}


@app.delete("/threads/{thread_id}")
def remove_thread(thread_id: str):
    delete_thread(thread_id)
    return {"deleted": thread_id}


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    """
    Server-Sent Events endpoint. Streams the assistant's response token
    by token as it's generated, then saves an auto-generated title the
    first time a thread is used.
    """

    def event_generator():
        # Auto-title new chats using the first message, same as before.
        current_title = load_thread_name(payload.thread_id)
        if current_title == "New Chat":
            title = generate_chat_title(payload.message)
            save_thread_title(payload.thread_id, title)
            yield f"event: title\ndata: {json.dumps({'title': title})}\n\n"

        full_response = ""

        for event in stream_chat_response(payload.thread_id, payload.message):
            if event["type"] == "tool_start":
                yield (
                    f"event: tool_start\n"
                    f"data: {json.dumps({'tool': event['tool']})}\n\n"
                )

            elif event["type"] == "tool_done":
                yield (
                    f"event: tool_done\n"
                    f"data: {json.dumps({'tool': event['tool']})}\n\n"
                )

            elif event["type"] == "token":
                full_response += event["content"]

                yield (
                    f"event: token\n"
                    f"data: {json.dumps({'content': event['content']})}\n\n"
                )

                yield (
                    f"event: done\n"
                    f"data: {json.dumps({'content': full_response})}\n\n"
                )

    return StreamingResponse(event_generator(), media_type="text/event-stream")