import { useEffect } from "react";
import { FiTrash2, FiX } from "react-icons/fi";

export default function ConfirmDeleteModal({
  open,
  title = "Delete Conversation",
  description = "This conversation will be permanently deleted. This action cannot be undone.",
  onCancel,
  onConfirm,
}) {
  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") {
        onCancel();
      }
    }

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
    >
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-icon">
            <FiTrash2 size={24} />
          </div>

          <button
            className="modal-close"
            onClick={onCancel}
            aria-label="Close"
          >
            <FiX size={20} />
          </button>
        </div>

        <h2>{title}</h2>

        <p>{description}</p>

        <div className="modal-actions">
          <button
            className="btn btn-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>

          <button
            className="btn btn-danger"
            onClick={onConfirm}
          >
            <FiTrash2 size={16} />
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}