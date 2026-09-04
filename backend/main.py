import json
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
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
from services.rag_service import ingest_pdf

app = FastAPI(title="Chatbot API")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


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


@app.post("/threads/{thread_id}/upload")
async def upload_pdf(thread_id: str, file: UploadFile = File(...)):
    """Index an uploaded PDF in the selected conversation's vector store."""
    filename = file.filename or "upload.pdf"
    is_pdf = file.content_type == "application/pdf" or filename.lower().endswith(".pdf")
    if not is_pdf:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        result = ingest_pdf(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=filename,
        )
        print(
            f"PDF indexed: thread_id={thread_id}, "
            f"filename={filename}, chunks={result['chunks']}"
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not process PDF: {exc}") from exc


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
