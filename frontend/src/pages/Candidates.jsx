import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, STATUSES } from "../api.js";
import { MatchBadge, Score, StatusBadge } from "../components/Badges.jsx";

export default function Candidates() {
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(null);

  const load = () =>
    api.listCandidates(jobId || null, status || null).then(setCandidates).catch((e) => setError(e.message));

  useEffect(() => { api.listJobs().then(setJobs).catch(() => {}); }, []);
  useEffect(() => { load(); }, [jobId, status]);

  const analyze = async (id) => {
    setAnalyzing(id);
    setError("");
    try {
      await api.analyze(id);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(null);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Candidate Analysis</h1>
        <p>Run AI screening to score each CV against its job description.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="toolbar">
        <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
          <option value="">All jobs</option>
          {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="card">
        {candidates.length === 0 ? (
          <div className="empty">No candidates found. <Link to="/upload">Upload CVs →</Link></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Job</th>
                <th>CV Score</th>
                <th>Match</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.id}>
                  <td><Link to={`/candidates/${c.id}`}>{c.name}</Link></td>
                  <td className="muted">{c.job_title}</td>
                  <td><Score value={c.cv_score} /></td>
                  <td><MatchBadge value={c.cv_recommendation} /></td>
                  <td><StatusBadge status={c.status} /></td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      className="btn small"
                      disabled={analyzing === c.id}
                      onClick={() => analyze(c.id)}
                    >
                      {analyzing === c.id ? "Analyzing…" : c.cv_score === null ? "Analyze CV" : "Re-analyze"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
