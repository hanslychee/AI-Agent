import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { Score, StatusBadge } from "../components/Badges.jsx";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-box">{error}</div>;
  if (!data) return <p className="muted">Loading…</p>;

  const stats = [
    { label: "Open Jobs", value: data.jobs },
    { label: "Candidates", value: data.candidates },
    { label: "CVs Analyzed", value: data.analyzed },
    { label: "Interviewed", value: data.interviewed },
    { label: "Final Reports", value: data.reports },
    { label: "Avg CV Score", value: data.average_cv_score ?? "—" },
  ];

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Recruitment pipeline at a glance.</p>
      </div>

      <div className="stat-grid">
        {stats.map((s) => (
          <div className="stat" key={s.label}>
            <div className="value">{s.value}</div>
            <div className="label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Pipeline by status</h2>
          <table>
            <tbody>
              {Object.entries(data.by_status).map(([status, count]) => (
                <tr key={status}>
                  <td><StatusBadge status={status} /></td>
                  <td style={{ textAlign: "right", fontWeight: 600 }}>{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h2>Recent candidates</h2>
          {data.recent_candidates.length === 0 ? (
            <div className="empty">
              No candidates yet. <Link to="/jobs">Add a job</Link> then{" "}
              <Link to="/upload">upload CVs</Link>.
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Job</th>
                  <th>CV Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_candidates.map((c) => (
                  <tr key={c.id}>
                    <td><Link to={`/candidates/${c.id}`}>{c.name}</Link></td>
                    <td className="muted">{c.job_title}</td>
                    <td><Score value={c.cv_score} /></td>
                    <td><StatusBadge status={c.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
