import { useState } from "react";
import { api, downloadReportPdf, HUMAN_REVIEW_REMINDER } from "../api.js";
import { MatchBadge, Score } from "../components/Badges.jsx";
import CandidatePicker from "../components/CandidatePicker.jsx";

export default function Reports() {
  const [candidate, setCandidate] = useState(null);
  const [salaryRange, setSalaryRange] = useState("");
  const [hrNotes, setHrNotes] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const select = async (id) => {
    setError("");
    setCandidate(null);
    if (!id) return;
    try {
      const c = await api.getCandidate(id);
      setCandidate(c);
      setSalaryRange(c.final_report?.salary_range || "");
      setHrNotes(c.final_report?.hr_notes || "");
    } catch (err) {
      setError(err.message);
    }
  };

  const run = async (label, fn) => {
    setBusy(label);
    setError("");
    try {
      setCandidate(await fn());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  };

  const report = candidate?.final_report;
  const content = report?.content || {};

  return (
    <>
      <div className="page-header">
        <h1>Final Reports</h1>
        <p>Combine the CV screening and interview evaluation into a final recruitment report.</p>
      </div>

      {error && <div className="error-box">{error}</div>}
      <CandidatePicker onSelect={select} />

      {candidate && (
        <div className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h2 style={{ margin: 0 }}>{candidate.name} — {candidate.job_title}</h2>
            <div className="row">
              <button
                className="btn small"
                disabled={!!busy}
                onClick={() => run("generate", () => api.generateReport(candidate.id))}
              >
                {busy === "generate" ? "Generating…" : report ? "Regenerate report" : "Generate report"}
              </button>
              {report && (
                <button className="btn secondary small" onClick={() => downloadReportPdf(candidate.id, candidate.name)}>
                  Export PDF
                </button>
              )}
            </div>
          </div>

          {(!candidate.analysis || !candidate.evaluation) && (
            <p className="muted" style={{ marginTop: 8 }}>
              The final report requires a completed CV analysis and interview evaluation.
            </p>
          )}

          {report && (
            <>
              <div className="stat-grid" style={{ marginTop: 14 }}>
                <div className="stat">
                  <div className="value"><Score value={candidate.cv_score} />/100</div>
                  <div className="label">CV match score</div>
                </div>
                <div className="stat">
                  <div className="value"><Score value={candidate.interview_score} />/100</div>
                  <div className="label">Interview score</div>
                </div>
                <div className="stat">
                  <div className="value"><MatchBadge value={report.recommendation} /></div>
                  <div className="label">Hiring recommendation</div>
                </div>
              </div>

              <h3>Executive summary</h3>
              <p>{content.executive_summary}</p>

              <div className="grid-2">
                <div>
                  <h3>Strengths</h3>
                  <ul className="clean">{(content.strengths || []).map((s) => <li key={s}>{s}</li>)}</ul>
                </div>
                <div>
                  <h3>Weaknesses</h3>
                  <ul className="clean">{(content.weaknesses || []).map((s) => <li key={s}>{s}</li>)}</ul>
                  <h3>Concerns</h3>
                  <ul className="clean">{(content.concerns || []).map((s) => <li key={s}>{s}</li>)}</ul>
                </div>
              </div>

              <h3>HR fields</h3>
              <label>Suggested salary range</label>
              <input
                value={salaryRange}
                onChange={(e) => setSalaryRange(e.target.value)}
                placeholder="e.g. 450,000 - 600,000 FCFA / month"
              />
              <label>Final HR notes</label>
              <textarea rows={3} value={hrNotes} onChange={(e) => setHrNotes(e.target.value)} />
              <div style={{ marginTop: 12 }}>
                <button
                  className="btn"
                  disabled={!!busy}
                  onClick={() => run("save", () => api.updateReport(candidate.id, { salary_range: salaryRange, hr_notes: hrNotes }))}
                >
                  {busy === "save" ? "Saving…" : "Save HR fields"}
                </button>
              </div>

              <p className="muted" style={{ marginTop: 14 }}>⚖️ {HUMAN_REVIEW_REMINDER}</p>
            </>
          )}
        </div>
      )}
    </>
  );
}
