const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function listThreads() {
  const res = await fetch(`${BASE_URL}/threads`);
  if (!res.ok) throw new Error("Failed to load threads");
  const data = await res.json();
  return data.threads;
}

export async function createThread() {
  const res = await fetch(`${BASE_URL}/threads`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create thread");
  return res.json();
}

export async function getMessages(threadId) {
  const res = await fetch(`${BASE_URL}/threads/${threadId}/messages`);
  if (!res.ok) throw new Error("Failed to load conversation");
  const data = await res.json();
  return data.messages;
}

export async function deleteThread(threadId) {
  const res = await fetch(`${BASE_URL}/threads/${threadId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete thread");
  return res.json();
}

/**
 * Streams a chat response via Server-Sent Events over POST.
 *
 * callbacks:
 *   onToken(text)   - called for each streamed content chunk
 *   onTitle(title)  - called once if the backend auto-generates a title
 *   onDone(fullText)- called when the stream completes
 */

export async function uploadDocument(threadId, file) {
  const formData = new FormData();

  formData.append("file", file);

  const res = await fetch(
    `${BASE_URL}/threads/${threadId}/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok)
    throw new Error("Upload failed");

  return res.json();
}
export async function streamChat(threadId,message,{onToken,onTitle,onToolStart,onToolDone,onDone})
 {  const res = await fetch(`${BASE_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, message }),
  });

  if (!res.ok || !res.body) {
    throw new Error("Failed to start chat stream");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE messages are separated by a blank line
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop(); // keep the last, possibly incomplete chunk

    for (const chunk of chunks) {
      const lines = chunk.split("\n");
      let eventType = "message";
      let dataLine = "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          eventType = line.replace("event:", "").trim();
        } else if (line.startsWith("data:")) {
          dataLine = line.replace("data:", "").trim();
        }
      }

      if (!dataLine) continue;
      const parsed = JSON.parse(dataLine);

      if (eventType === "token" && onToken)
    onToken(parsed.content);

    if (eventType === "title" && onTitle) onTitle(parsed.title);

    if (eventType === "tool_start" && onToolStart) onToolStart(parsed.tool);

    if (eventType === "tool_done" && onToolDone) onToolDone(parsed.tool);

    if (eventType === "done" && onDone) onDone(parsed.content);
    }
  }
}