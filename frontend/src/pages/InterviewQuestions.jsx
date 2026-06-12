import { useState } from "react";
import { api } from "../api.js";
import CandidatePicker from "../components/CandidatePicker.jsx";

const SECTIONS = [
  ["technical", "Technical questions"],
  ["behavioral", "Behavioral questions"],
  ["experience_based", "Experience-based questions"],
  ["culture_fit", "Culture-fit questions"],
  ["practical_case", "Practical case questions"],
];

export default function InterviewQuestions() {
  const [candidate, setCandidate] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const select = async (id) => {
    setError("");
    setCandidate(null);
    if (!id) return;
    try {
      setCandidate(await api.getCandidate(id));
    } catch (err) {
      setError(err.message);
    }
  };

  const generate = async () => {
    setBusy(true);
    setError("");
    try {
      setCandidate(await api.generateQuestions(candidate.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Interview Questions</h1>
        <p>Tailored questions based on the job description, the CV, and the screening's missing-skill findings.</p>
      </div>

      {error && <div className="error-box">{error}</div>}
      <CandidatePicker onSelect={select} />

      {candidate && (
        <div className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h2 style={{ margin: 0 }}>{candidate.name} — {candidate.job_title}</h2>
            <button className="btn small" disabled={busy} onClick={generate}>
              {busy ? "Generating…" : candidate.questions ? "Regenerate questions" : "Generate questions"}
            </button>
          </div>

          {!candidate.analysis && (
            <p className="muted" style={{ marginTop: 8 }}>
              Tip: run the CV analysis first so questions can target missing skills.
            </p>
          )}

          {candidate.questions ? (
            SECTIONS.map(([key, title]) => (
              <div key={key}>
                <h3>{title}</h3>
                {(candidate.questions[key] || []).map((q, i) => (
                  <div className="question-item" key={i}>
                    <div>{q.question}</div>
                    <div className="follow-up">↳ Follow-up: {q.follow_up}</div>
                  </div>
                ))}
              </div>
            ))
          ) : (
            <p className="muted" style={{ marginTop: 10 }}>No questions generated yet.</p>
          )}
        </div>
      )}
    </>
  );
}
