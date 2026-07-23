import ToolStatusPill from "./ToolStatusPill";

export default function MessageBubble({
  role,
  content,
  isStreaming,
  toolStatus,
}) {
  const isUser = role === "user";

  return (
    <div
      className={`message ${
        isUser ? "message--user" : "message--assistant"
      }`}
    >
      <div className="message__role">
        {isUser ? "You" : "Assistant"}
      </div>

      <div className="message__bubble">

        {!isUser && isStreaming && toolStatus && (
          <ToolStatusPill status={toolStatus} />
        )}

        <div className="message__content">
          {content}
          {isStreaming && (
            <span className="cursor" aria-hidden="true" />
          )}
        </div>

      </div>
    </div>
  );
}