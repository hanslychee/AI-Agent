import { useEffect, useState } from "react";
import { api } from "../api.js";

function JobCard({ job, onDelete }) {
  const [open, setOpen] = useState(false);
  const x = job.extracted || {};
  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <div>
          <strong>{job.title}</strong>{" "}
          <span className="muted">· {job.candidate_count} candidate(s)</span>
        </div>
        <div className="row">
          <button className="btn secondary small" onClick={() => setOpen(!open)}>
            {open ? "Hide details" : "View details"}
          </button>
          <button className="btn danger small" onClick={() => onDelete(job.id)}>
            Delete
          </button>
        </div>
      </div>
      {open && (
        <div style={{ marginTop: 10 }}>
          <h3>Required skills</h3>
          <div className="tag-list">{(x.required_skills || []).map((s) => <span className="tag" key={s}>{s}</span>)}</div>
          <h3>Preferred skills</h3>
          <div className="tag-list">{(x.preferred_skills || []).map((s) => <span className="tag" key={s}>{s}</span>)}</div>
          <h3>Experience & education</h3>
          <p style={{ margin: "4px 0" }}>
            Minimum {x.years_of_experience ?? 0} year(s) of experience.
          </p>
          <ul className="clean">{(x.education_requirements || []).map((e) => <li key={e}>{e}</li>)}</ul>
          <h3>Responsibilities</h3>
          <ul className="clean">{(x.responsibilities || []).map((r) => <li key={r}>{r}</li>)}</ul>
          <h3>Soft skills</h3>
          <div className="tag-list">{(x.soft_skills || []).map((s) => <span className="tag" key={s}>{s}</span>)}</div>
          <h3>Evaluation criteria</h3>
          <ul className="clean">{(x.evaluation_criteria || []).map((c) => <li key={c}>{c}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => api.listJobs().then(setJobs).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const job = await api.createJob(description);
      setSuccess(`Job "${job.title}" added — requirements extracted automatically.`);
      setDescription("");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id) => {
    if (!confirm("Delete this job and all of its candidates?")) return;
    try {
      await api.deleteJob(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Job Descriptions</h1>
        <p>Paste a job description — the assistant extracts title, skills, experience and evaluation criteria.</p>
      </div>

      {error && <div className="error-box">{error}</div>}
      {success && <div className="success-box">{success}</div>}

      <form className="card" onSubmit={submit}>
        <h2>Add a job description</h2>
        <textarea
          rows={10}
          placeholder="Paste the full job description here (minimum 30 characters)…"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div style={{ marginTop: 12 }}>
          <button className="btn" disabled={busy || description.trim().length < 30}>
            {busy ? "Extracting with AI…" : "Add job & extract requirements"}
          </button>
        </div>
      </form>

      {jobs.length === 0 ? (
        <div className="card empty">No jobs yet. Add your first job description above.</div>
      ) : (
        jobs.map((job) => <JobCard key={job.id} job={job} onDelete={remove} />)
      )}
    </>
  );
}
