import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api.js";

/**
 * Shared candidate selector used by the Questions / Evaluation / Reports pages.
 * Reads ?candidate=<id> from the URL so other pages can deep-link.
 */
export default function CandidatePicker({ onSelect }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [candidates, setCandidates] = useState([]);
  const selected = searchParams.get("candidate") || "";

  useEffect(() => {
    api.listCandidates().then((list) => {
      setCandidates(list);
      if (selected) onSelect(Number(selected));
    }).catch(() => {});
  }, []);

  const change = (e) => {
    const value = e.target.value;
    setSearchParams(value ? { candidate: value } : {});
    onSelect(value ? Number(value) : null);
  };

  return (
    <div className="toolbar">
      <select value={selected} onChange={change}>
        <option value="">Select a candidate…</option>
        {candidates.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name} — {c.job_title}
          </option>
        ))}
      </select>
    </div>
  );
}
