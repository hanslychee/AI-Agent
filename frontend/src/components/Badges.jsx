const STATUS_COLORS = {
  New: "gray",
  Shortlisted: "",
  "Interview Scheduled": "amber",
  Interviewed: "amber",
  Recommended: "green",
  Rejected: "red",
  Hired: "green",
};

const MATCH_COLORS = {
  "Strong Match": "green",
  "Good Match": "",
  "Average Match": "amber",
  "Weak Match": "red",
  "Highly Recommended": "green",
  Recommended: "green",
  "Consider with Caution": "amber",
  "Not Recommended": "red",
};

export function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_COLORS[status] ?? "gray"}`}>{status}</span>;
}

export function MatchBadge({ value }) {
  if (!value) return <span className="muted">—</span>;
  return <span className={`badge ${MATCH_COLORS[value] ?? ""}`}>{value}</span>;
}

export function Score({ value }) {
  if (value === null || value === undefined) return <span className="muted">—</span>;
  const color = value >= 80 ? "var(--green)" : value >= 65 ? "var(--primary)" : value >= 50 ? "var(--amber)" : "var(--red)";
  return (
    <span className="score-pill" style={{ color }}>
      {value}
    </span>
  );
}
