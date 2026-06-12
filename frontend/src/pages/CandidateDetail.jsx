import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, downloadReportPdf, STATUSES } from "../api.js";
import { MatchBadge, Score, StatusBadge } from "../components/Badges.jsx";

const SCORE_LABELS = {
  required_skills_match: "Required skills match (30)",
  relevant_experience: "Relevant experience (25)",
  education_certifications: "Education & certifications (15)",
  achievements_projects: "Achievements & projects (15)",
  soft_skills_communication: "Soft skills & communication (10)",
  overall_role_fit: "Overall role fit (5)",
};

export default function CandidateDetail() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  const load = () => api.getCandidate(id).then(setC).catch((e) => setError(e.message));
  useEffect(() => { load(); }, [id]);

  const run = async (label, fn) => {
    setBusy(label);
    setError("");
    try {
      setC(await fn());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  };

  if (error && !c) return <div className="error-box">{error}</div>;
  if (!c) return <p className="muted">Loading…</p>;

  const cv = c.parsed_cv || {};
  const analysis = c.analysis;
  const summary = analysis?.summary;

  return (
    <>
      <div className="page-header">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div>
            <h1>{c.name}</h1>
            <p>
              {c.job_title} · {c.email || "no email"} {c.phone ? `· ${c.phone}` : ""}
            </p>
          </div>
          <div className="row">
            <select
              value={c.status}
              onChange={(e) => run("status", () => api.updateStatus(c.id, e.target.value).then(() => api.getCandidate(id)))}
              style={{ width: "auto" }}
            >
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </select>
            <StatusBadge status={c.status} />
          </div>
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="card">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <h2 style={{ margin: 0 }}>CV screening</h2>
          <button className="btn small" disabled={!!busy} onClick={() => run("analyze", () => api.analyze(c.id))}>
            {busy === "analyze" ? "Analyzing…" : analysis ? "Re-run analysis" : "Run AI analysis"}
          </button>
        </div>

        {analysis ? (
          <>
            <div className="stat-grid" style={{ marginTop: 14 }}>
              <div className="stat">
                <div className="value"><Score value={analysis.total_score} />/100</div>
                <div className="label">CV match score</div>
              </div>
              <div className="stat">
                <div className="value">{analysis.match_percentage}%</div>
                <div className="label">Match percentage</div>
              </div>
              <div className="stat">
                <div className="value"><MatchBadge value={analysis.recommendation} /></div>
                <div className="label">Recommendation</div>
              </div>
            </div>

            <div className="grid-2">
              <div>
                <h3>Score breakdown</h3>
                <table>
                  <tbody>
                    {Object.entries(SCORE_LABELS).map(([key, label]) => (
                      <tr key={key}>
                        <td>{label}</td>
                        <td style={{ textAlign: "right", fontWeight: 600 }}>{analysis.scores?.[key]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div>
                <h3>Key strengths</h3>
                <ul className="clean">{(analysis.key_strengths || []).map((s) => <li key={s}>{s}</li>)}</ul>
                <h3>Missing skills</h3>
                <ul className="clean">{(analysis.missing_skills || []).map((s) => <li key={s}>{s}</li>)}</ul>
                <h3>Risk factors</h3>
                <ul className="clean">{(analysis.risk_factors || []).map((s) => <li key={s}>{s}</li>)}</ul>
              </div>
            </div>

            {summary && (
              <>
                <h3>Candidate summary</h3>
                <p>{summary.overview}</p>
                <p><strong>Best matching experience:</strong> {summary.best_matching_experience}</p>
                <div className="grid-2">
                  <div>
                    <strong>Top strengths</strong>
                    <ul className="clean">{(summary.top_strengths || []).map((s) => <li key={s}>{s}</li>)}</ul>
                  </div>
                  <div>
                    <strong>Possible concerns</strong>
                    <ul className="clean">{(summary.possible_concerns || []).map((s) => <li key={s}>{s}</li>)}</ul>
                  </div>
                </div>
                <p><strong>Suggested next step:</strong> {summary.suggested_next_step}</p>
              </>
            )}
          </>
        ) : (
          <p className="muted" style={{ marginTop: 10 }}>Not analyzed yet — run the AI analysis to score this CV against the job.</p>
        )}
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Parsed CV</h2>
          <h3>Skills</h3>
          <div className="tag-list">{(cv.skills || []).map((s) => <span className="tag" key={s}>{s}</span>)}</div>
          <h3>Work experience</h3>
          {(cv.work_experience || []).map((w, i) => (
            <p key={i} style={{ margin: "4px 0" }}>
              <strong>{w.title}</strong> — {w.company} <span className="muted">({w.period})</span>
              <br /><span className="muted">{w.description}</span>
            </p>
          ))}
          <h3>Education</h3>
          {(cv.education || []).map((e, i) => (
            <p key={i} style={{ margin: "4px 0" }}>{e.degree} — {e.institution} <span className="muted">({e.period})</span></p>
          ))}
          {(cv.certifications || []).length > 0 && (<><h3>Certifications</h3><ul className="clean">{cv.certifications.map((x) => <li key={x}>{x}</li>)}</ul></>)}
          {(cv.projects || []).length > 0 && (<><h3>Projects</h3><ul className="clean">{cv.projects.map((x) => <li key={x}>{x}</li>)}</ul></>)}
          {(cv.achievements || []).length > 0 && (<><h3>Achievements</h3><ul className="clean">{cv.achievements.map((x) => <li key={x}>{x}</li>)}</ul></>)}
          {(cv.languages || []).length > 0 && (<><h3>Languages</h3><div className="tag-list">{cv.languages.map((x) => <span className="tag" key={x}>{x}</span>)}</div></>)}
          {(cv.career_timeline || []).length > 0 && (<><h3>Career timeline</h3><ul className="clean">{cv.career_timeline.map((x) => <li key={x}>{x}</li>)}</ul></>)}
        </div>

        <div className="card">
          <h2>Next steps</h2>
          <p className="muted">Continue this candidate's process:</p>
          <div className="row" style={{ flexDirection: "column", alignItems: "stretch", gap: 8 }}>
            <Link className="btn secondary" to={`/questions?candidate=${c.id}`}>Interview questions {c.has_questions ? "✓" : "→"}</Link>
            <Link className="btn secondary" to={`/evaluation?candidate=${c.id}`}>Interview evaluation {c.interview_score !== null ? `✓ (${c.interview_score}/100)` : "→"}</Link>
            <Link className="btn secondary" to={`/reports?candidate=${c.id}`}>Final report {c.has_report ? "✓" : "→"}</Link>
            {c.has_report && (
              <button className="btn" onClick={() => downloadReportPdf(c.id, c.name)}>Export report as PDF</button>
            )}
          </div>

          {c.evaluation && (
            <>
              <h3>Interview evaluation summary</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{c.evaluation.ai_summary}</p>
            </>
          )}
        </div>
      </div>
    </>
  );
}
