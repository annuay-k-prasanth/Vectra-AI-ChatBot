import { Plus } from "lucide-react";
import ThreadItem from "./ThreadItem";

export default function Sidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewChat,
  onRenameThread,
  onDownloadThread,
  onDeleteThread,
  onChangeBackground,
  isOpen,
}) {
  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <div className="sidebar__header">
        <img
          src="/logo.png"
          alt="ChatBot"
          className="sidebar__logo-image"
        />

        <h2 className="sidebar__title">
          VECTRA AI
        </h2>

        <p className="sidebar__subtitle">
          AI ChatBot
        </p>

        <button
          className="btn btn--new"
          onClick={onNewChat}
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>

      </div>

      <div className="sidebar__label">
        Threads
      </div>

      <nav className="sidebar__list">
        {threads.length === 0 ? (
          <p className="sidebar__empty">
            No conversations yet. Start one.
          </p>
        ) : (
          threads.map((thread) => (
            <ThreadItem
              key={thread.thread_id}
              thread={thread}
              active={thread.thread_id === activeThreadId}
              onSelect={onSelectThread}
              onRename={onRenameThread}
              onDownload={onDownloadThread}
              onDelete={onDeleteThread}
              onChangeBackground={onChangeBackground}
            />
          ))
        )}
      </nav>
    </aside>
  );
}