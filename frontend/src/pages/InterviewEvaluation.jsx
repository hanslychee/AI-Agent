import { useState } from "react";
import { api } from "../api.js";
import CandidatePicker from "../components/CandidatePicker.jsx";

const CATEGORIES = [
  ["technical_skills", "Technical skills"],
  ["problem_solving", "Problem-solving"],
  ["communication", "Communication"],
  ["relevant_experience", "Relevant experience"],
  ["motivation", "Motivation"],
  ["team_fit", "Team fit"],
  ["leadership_potential", "Leadership potential"],
  ["overall_impression", "Overall impression"],
];

function RatingRow({ label, value, onChange }) {
  return (
    <div className="rating-row">
      <span>{label}</span>
      <div className="stars">
        {[1, 2, 3, 4, 5].map((n) => (
          <button type="button" key={n} className={value >= n ? "on" : ""} onClick={() => onChange(n)}>
            {n}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function InterviewEvaluation() {
  const [candidate, setCandidate] = useState(null);
  const [ratings, setRatings] = useState({});
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const select = async (id) => {
    setError("");
    setCandidate(null);
    if (!id) return;
    try {
      const c = await api.getCandidate(id);
      setCandidate(c);
      setRatings(c.evaluation?.ratings || {});
      setNotes(c.evaluation?.interviewer_notes || "");
    } catch (err) {
      setError(err.message);
    }
  };

  const complete = CATEGORIES.every(([key]) => ratings[key] >= 1);

  const submit = async () => {
    setBusy(true);
    setError("");
    try {
      setCandidate(await api.submitEvaluation(candidate.id, ratings, notes));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Interview Evaluation</h1>
        <p>Rate each category from 1 (poor) to 5 (excellent). The assistant computes the score and writes a short evaluation.</p>
      </div>

      {error && <div className="error-box">{error}</div>}
      <CandidatePicker onSelect={select} />

      {candidate && (
        <div className="grid-2">
          <div className="card">
            <h2>Scorecard — {candidate.name}</h2>
            {CATEGORIES.map(([key, label]) => (
              <RatingRow
                key={key}
                label={label}
                value={ratings[key] || 0}
                onChange={(v) => setRatings({ ...ratings, [key]: v })}
              />
            ))}
            <label>Interviewer notes</label>
            <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)}
              placeholder="Observations from the interview (optional)…" />
            <div style={{ marginTop: 12 }}>
              <button className="btn" disabled={busy || !complete} onClick={submit}>
                {busy ? "Saving & summarizing…" : "Save evaluation"}
              </button>
              {!complete && <span className="muted" style={{ marginLeft: 10 }}>Rate all categories to submit.</span>}
            </div>
          </div>

          <div className="card">
            <h2>Result</h2>
            {candidate.evaluation ? (
              <>
                <div className="stat" style={{ marginBottom: 12 }}>
                  <div className="value">{candidate.evaluation.score}/100</div>
                  <div className="label">Interview score</div>
                </div>
                <h3>AI evaluation summary</h3>
                <p style={{ whiteSpace: "pre-wrap" }}>{candidate.evaluation.ai_summary}</p>
              </>
            ) : (
              <p className="muted">No evaluation submitted yet.</p>
            )}
          </div>
        </div>
      )}
    </>
  );
}
