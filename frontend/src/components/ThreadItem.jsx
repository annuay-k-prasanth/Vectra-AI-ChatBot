import { useEffect, useRef, useState } from "react";
import { MoreHorizontal } from "lucide-react";
import ThreadMenu from "./ThreadMenu";

export default function ThreadItem({
  thread,
  active,
  onSelect,
  onRename,
  onDownload,
  onDelete,
  onChangeBackground,
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  const menuRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () =>
      document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleBackgroundSelected(e) {
    const file = e.target.files?.[0];

    if (!file) return;

    onChangeBackground(thread, file);

    e.target.value = "";
  }

  return (
    <div
      className={`thread-item ${active ? "active" : ""}`}
      onClick={() => onSelect(thread.thread_id)}
    >
      <span className="thread-title">
        {thread.title}
      </span>

      <div className="thread-actions" ref={menuRef}>
        <button
          className="menu-btn"
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpen((prev) => !prev);
          }}
        >
          <MoreHorizontal size={18} />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={handleBackgroundSelected}
        />

        {menuOpen && (
          <ThreadMenu
            onRename={() => {
              setMenuOpen(false);
              onRename(thread);
            }}

            onDownload={() => {
              setMenuOpen(false);
              onDownload(thread);
            }}

            onDelete={() => {
              setMenuOpen(false);
              onDelete(thread);
            }}

            onChangeBackground={() => {
              setMenuOpen(false);
              fileInputRef.current?.click();
            }}
          />
        )}
      </div>
    </div>
  );
}