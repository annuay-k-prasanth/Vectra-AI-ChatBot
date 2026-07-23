export default function downloadChat(threadTitle, messages) {
  const now = new Date();

  const date = now.toLocaleString();

  let content = "";

  content += `${threadTitle}\n`;
  content += `${"=".repeat(threadTitle.length)}\n\n`;

  content += `Exported: ${date}\n\n`;

  messages.forEach((message, index) => {
    content += `──────────────────────────────\n`;

    content += `${index + 1}. ${
        message.role === "user"
        ? "👤 You"
        : "🤖 Assistant"
    }\n`;

    content += `──────────────────────────────\n`;

    content += `${message.content}\n\n`;
    });

  const blob = new Blob(
    [content],
    { type: "text/plain;charset=utf-8" }
  );

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;

  link.download = `${threadTitle}.txt`;

  document.body.appendChild(link);

  link.click();

  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}