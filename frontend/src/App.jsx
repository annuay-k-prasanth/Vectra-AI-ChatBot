import { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import ConfirmDeleteModal from "./components/ConfirmDeleteModal.jsx";
import downloadChat from "./utils/downloadChat";

import {
  listThreads,
  createThread,
  getMessages,
  deleteThread,
  streamChat,
} from "./api/chatApi.js";

export default function App() {
  const [threads, setThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolStatus, setToolStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatBackground, setChatBackground] = useState(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [threadToDelete, setThreadToDelete] = useState(null);

  // ----------------------------
  // Load Threads
  // ----------------------------

  useEffect(() => {
    (async () => {
      const existing = await listThreads();
      setThreads(existing);

      if (existing.length > 0) {
        setActiveThreadId(existing[0].thread_id);

        const history = await getMessages(existing[0].thread_id);
        setMessages(history);
      }
    })();
  }, []);

  // ----------------------------
  // New Chat
  // ----------------------------

  const handleNewChat = useCallback(() => {
    setActiveThreadId(null);
    setMessages([]);
    setSidebarOpen(false);
  }, []);

  // ----------------------------
  // Select Thread
  // ----------------------------

  const handleSelectThread = useCallback(async (threadId) => {
    setActiveThreadId(threadId);

    const history = await getMessages(threadId);

    setMessages(history);

    setSidebarOpen(false);
  }, []);

  // ----------------------------
  // Delete Thread
  // ----------------------------

  const handleDeleteThread = useCallback((thread) => {
    setThreadToDelete(thread);
    setDeleteDialogOpen(true);
  }, []);

  const confirmDeleteThread = useCallback(async () => {
    if (!threadToDelete) return;

    await deleteThread(threadToDelete.thread_id);

    const remaining = threads.filter(
      (t) => t.thread_id !== threadToDelete.thread_id
    );

    setThreads(remaining);

    if (threadToDelete.thread_id === activeThreadId) {
      if (remaining.length > 0) {
        const next = remaining[0];

        setActiveThreadId(next.thread_id);

        const history = await getMessages(next.thread_id);

        setMessages(history);
      } else {
        setActiveThreadId(null);
        setMessages([]);
      }
    }

    setDeleteDialogOpen(false);
    setThreadToDelete(null);
  }, [
    threadToDelete,
    activeThreadId,
    threads,
  ]);

  // ----------------------------
  // Download
  // ----------------------------

  const handleDownloadThread = useCallback(
    (thread) => {
      downloadChat(thread.title, messages);
    },
    [messages]
  );

  // ----------------------------
  // Rename
  // ----------------------------

  const handleRenameThread = useCallback((thread) => {
    const title = prompt("Rename conversation", thread.title);

    if (!title?.trim()) return;

    setThreads((prev) =>
      prev.map((t) =>
        t.thread_id === thread.thread_id
          ? { ...t, title: title.trim() }
          : t
      )
    );
  }, []);

  // ----------------------------
  // Send Message
  // ----------------------------

  const handleSendMessage = useCallback(
    async (text) => {

      let threadId = activeThreadId;

      // Create thread only when sending the first message
      if (!threadId) {
        const thread = await createThread();

        threadId = thread.thread_id;

        setThreads((prev) => [thread, ...prev]);

        setActiveThreadId(threadId);
      }

      setMessages((prev) => [
        ...prev,
        { role: "user", content: text },
        { role: "assistant", content: "" },
      ]);

      setIsStreaming(true);

      try {
        await streamChat(threadId, text, {
          onTitle: (title) => {
            setThreads((prev) =>
              prev.map((t) =>
                t.thread_id === threadId
                  ? { ...t, title }
                  : t
              )
            );
          },

          onToolStart: (tool) => {
            setToolStatus({
              tool,
              phase: "calling",
            });
          },

          onToolDone: (tool) => {
            setToolStatus({
              tool,
              phase: "done",
            });

            setTimeout(() => {
              setToolStatus(null);
            }, 1000);
          },

          onToken: (chunk) => {
            setMessages((prev) => {
              const updated = [...prev];

              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                content:
                  updated[updated.length - 1].content + chunk,
              };

              return updated;
            });
          },

          onDone: () => {
            setIsStreaming(false);
          },
        });
      } catch (err) {
        console.error(err);
        setIsStreaming(false);
      }
    },
    [activeThreadId]
  );

  // ----------------------------
// Change Background
// ----------------------------

  const handleChangeBackground = useCallback((thread, file) => {
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);

    setChatBackground(imageUrl);
  }, []);

  return (
    <div className="app">
      <Sidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onNewChat={handleNewChat}
        onRenameThread={handleRenameThread}
        onDownloadThread={handleDownloadThread}
        onDeleteThread={handleDeleteThread}
        onChangeBackground={handleChangeBackground}
        isOpen={sidebarOpen}
      />

      <ChatWindow
        messages={messages}
        toolStatus={toolStatus}
        background={chatBackground}
        onSendMessage={handleSendMessage}
        isStreaming={isStreaming}
        onToggleSidebar={() =>
          setSidebarOpen((prev) => !prev)
        }

      />

      <ConfirmDeleteModal
        open={deleteDialogOpen}
        onCancel={() => {
          setDeleteDialogOpen(false);
          setThreadToDelete(null);
        }}
        onConfirm={confirmDeleteThread}
      />
    </div>
  );
}