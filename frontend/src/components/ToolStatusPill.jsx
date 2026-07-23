const labels = {
  get_stock_price: "📈 Fetching stock price...",
  calculator: "🧮 Calculating...",
  search_tool: "🔎 Searching...",
  duckduckgo_search: "🔎 Searching the web...",
};

export default function ToolStatusPill({ status }) {
  if (!status) return null;

  const label = labels[status.tool] ?? `🔧 ${status.tool}`;

  return (
    <div className={`tool-pill ${status.phase}`}>
      {status.phase === "calling" ? label : `✅ ${label}`}
    </div>
  );
}