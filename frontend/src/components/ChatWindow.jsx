import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble.jsx";
import { Paperclip, FileText, X } from "lucide-react";

export default function ChatWindow({
  messages,
  toolStatus,
  background,
  onSendMessage,
  isStreaming,
  onToggleSidebar,
  onUploadDocument,
  uploadedDocument,
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);

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

  function handleFileSelected(e) {
    const file = e.target.files?.[0];

    if (!file) return;

    if (typeof onUploadDocument === "function") {
      onUploadDocument(file);
    }

    e.target.value = "";
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

      {/* Uploaded PDF */}
      {uploadedDocument && (
        <div className="document-chip">
          <div className="document-chip-left">
            <FileText size={20} />
            <span>{uploadedDocument}</span>
          </div>

          <button
            type="button"
            className="document-remove"
          >
            <X size={18} />
          </button>
        </div>
      )}

      <form
        className="chat__input-bar"
        onSubmit={handleSubmit}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={handleFileSelected}
        />

        <button
          type="button"
          className="attach-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isStreaming}
          title="Upload PDF"
        >
          <Paperclip size={22} color="white" />
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type here..."
          disabled={isStreaming}
        />

        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
        >
          Send
        </button>
      </form>
    </main>
  );
}