import {
  Pencil,
  Download,
  Trash2,
  Image,
} from "lucide-react";

export default function ThreadMenu({
  onRename,
  onDownload,
  onDelete,
  onChangeBackground,
}) {
  return (
    <div className="thread-menu">

      <button
        className="thread-menu-item"
        onClick={onRename}
      >
        <Pencil size={16} />
        <span>Rename</span>
      </button>

      <button
        className="thread-menu-item"
        onClick={onChangeBackground}
      >
        <Image size={16} />
        <span>Change Background</span>
      </button>

      <button
        className="thread-menu-item"
        onClick={onDownload}
      >
        <Download size={16} />
        <span>Download Chat</span>
      </button>

      <button
        className="thread-menu-item danger"
        onClick={onDelete}
      >
        <Trash2 size={16} />
        <span>Delete Chat</span>
      </button>

    </div>
  );
}