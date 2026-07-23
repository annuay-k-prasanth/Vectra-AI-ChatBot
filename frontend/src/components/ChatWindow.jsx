import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatWindow({
  messages,
  toolStatus,
  background,
  onSendMessage,
  isStreaming,
  onToggleSidebar,
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  function handleSubmit(e) {
    e.preventDefault();

    const trimmed = input.trim();

    if (!trimmed || isStreaming) return;

    onSendMessage(trimmed);
    setInput("");
  }

  return (
    <main
      className="chat"
      style={{
        backgroundImage: background
          ? `url(${background})`
          : "none",
      }}
    >
      <div className="chat__topbar">
        <button
          className="hamburger"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          ☰
        </button>
      </div>

      <div
        className="chat__messages"
        ref={scrollRef}
      >
        {messages.length === 0 && (
          <div className="chat__intro">
            <h1>START A CHAT WITH VECTRA</h1>
            <p>What are we working on?</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            content={msg.content}
            toolStatus={toolStatus}
            isStreaming={
              isStreaming &&
              i === messages.length - 1 &&
              msg.role === "assistant"
            }
          />
        ))}
      </div>

      <form
        className="chat__input-bar"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type here..."
          disabled={isStreaming}
        />

        <button
          type="submit"
          disabled={
            isStreaming || !input.trim()
          }
        >
          Send
        </button>
      </form>
    </main>
  );
}