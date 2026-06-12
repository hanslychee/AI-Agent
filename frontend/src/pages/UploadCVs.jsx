import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

export default function UploadCVs() {
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState("");
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.listJobs().then((list) => {
      setJobs(list);
      if (list.length) setJobId(String(list[0].id));
    }).catch((e) => setError(e.message));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const res = await api.uploadCVs(jobId, files);
      setResult(res);
      setFiles([]);
      e.target.reset?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Upload CVs</h1>
        <p>Upload one or more CVs (PDF, DOCX or TXT). Each CV is parsed and structured by the assistant.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      {jobs.length === 0 ? (
        <div className="card empty">
          You need a job first. <Link to="/jobs">Add a job description →</Link>
        </div>
      ) : (
        <form className="card" onSubmit={submit}>
          <label>Job</label>
          <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title}</option>
            ))}
          </select>

          <label>CV files</label>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={(e) => setFiles(Array.from(e.target.files))}
          />

          <div style={{ marginTop: 14 }}>
            <button className="btn" disabled={busy || !files.length || !jobId}>
              {busy ? `Parsing ${files.length} CV(s) with AI…` : `Upload & parse ${files.length || ""} CV(s)`}
            </button>
          </div>
        </form>
      )}

      {result && (
        <div className="card">
          <h2>Upload results</h2>
          {result.created.length > 0 && (
            <>
              <div className="success-box">{result.created.length} candidate(s) created.</div>
              <table>
                <thead>
                  <tr><th>Name</th><th>Email</th><th>File</th><th></th></tr>
                </thead>
                <tbody>
                  {result.created.map((c) => (
                    <tr key={c.id}>
                      <td>{c.name}</td>
                      <td className="muted">{c.email || "—"}</td>
                      <td className="muted">{c.source_filename}</td>
                      <td><Link to={`/candidates/${c.id}`}>Open →</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          {result.errors.length > 0 && (
            <div className="error-box" style={{ marginTop: 12 }}>
              {result.errors.map((e) => (
                <div key={e.filename}><strong>{e.filename}</strong>: {e.error}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
}
