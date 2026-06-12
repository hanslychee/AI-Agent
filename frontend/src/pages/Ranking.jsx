import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, STATUSES } from "../api.js";
import { MatchBadge, Score, StatusBadge } from "../components/Badges.jsx";

export default function Ranking() {
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState("");
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => { api.listJobs().then(setJobs).catch(() => {}); }, []);
  useEffect(() => {
    api.ranking(jobId || null).then(setRows).catch((e) => setError(e.message));
  }, [jobId]);

  const changeStatus = async (id, status) => {
    try {
      await api.updateStatus(id, status);
      setRows(await api.ranking(jobId || null));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Candidate Ranking</h1>
        <p>Final score = 60% CV match + 40% interview score. Ranking is a decision aid, not a decision.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="toolbar">
        <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
          <option value="">All jobs</option>
          {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
        </select>
      </div>

      <div className="card">
        {rows.length === 0 ? (
          <div className="empty">No candidates to rank yet.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Job</th>
                <th>CV Score</th>
                <th>Interview</th>
                <th>Final Score</th>
                <th>Recommendation</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c, i) => (
                <tr key={c.id}>
                  <td className="muted">{i + 1}</td>
                  <td><Link to={`/candidates/${c.id}`}>{c.name}</Link></td>
                  <td className="muted">{c.job_title}</td>
                  <td><Score value={c.cv_score} /></td>
                  <td><Score value={c.interview_score} /></td>
                  <td><Score value={c.final_score} /></td>
                  <td><MatchBadge value={c.report_recommendation || c.cv_recommendation} /></td>
                  <td>
                    <select
                      value={c.status}
                      onChange={(e) => changeStatus(c.id, e.target.value)}
                      style={{ width: "auto", padding: "4px 6px" }}
                    >
                      {STATUSES.map((s) => <option key={s}>{s}</option>)}
                    </select>
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
