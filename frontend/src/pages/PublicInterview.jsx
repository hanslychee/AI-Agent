import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api.js";

/** Candidate-facing AI interview chat. Reached via the tokenized link — no login. */
export default function PublicInterview() {
  const { token } = useParams();
  const [session, setSession] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [fatal, setFatal] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    api.getPublicInterview(token)
      .then(setSession)
      .catch((e) => setFatal(e.message));
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.transcript?.length, busy]);

  const start = async () => {
    setBusy(true);
    setError("");
    try {
      setSession(await api.startPublicInterview(token));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const send = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setBusy(true);
    setError("");
    // Show the candidate's message immediately while the interviewer "types".
    setSession((s) => ({ ...s, transcript: [...s.transcript, { role: "candidate", text }] }));
    setInput("");
    try {
      setSession(await api.sendPublicInterviewMessage(token, text));
    } catch (err) {
      setError(err.message);
      setSession((s) => ({ ...s, transcript: s.transcript.slice(0, -1) }));
      setInput(text);
    } finally {
      setBusy(false);
    }
  };

  if (fatal) {
    return (
      <div className="interview-wrap">
        <div className="interview-card">
          <h1>Interview unavailable</h1>
          <p className="muted">{fatal}</p>
        </div>
      </div>
    );
  }
  if (!session) {
    return (
      <div className="interview-wrap">
        <div className="interview-card"><p className="muted">Loading…</p></div>
      </div>
    );
  }

  const completed = session.status === "completed";

  return (
    <div className="interview-wrap">
      <div className="interview-card">
        <div className="interview-header">
          <h1>Interview — {session.job_title}</h1>
          <p className="muted">
            Hello {session.candidate_name}. This is a structured text interview conducted by an
            AI assistant on behalf of the hiring team. Your answers are recorded and reviewed by
            a human recruiter — no hiring decision is made by the AI.
          </p>
        </div>

        {session.status === "pending" ? (
          <div className="interview-start">
            <p>
              The interview takes about 15–25 minutes (roughly 8–12 questions). Answer in your
              own words; you can take your time. Ready when you are.
            </p>
            <button className="btn" onClick={start} disabled={busy}>
              {busy ? "Starting…" : "Start interview"}
            </button>
          </div>
        ) : (
          <>
            <div className="chat">
              {session.transcript.map((m, i) => (
                <div key={i} className={`bubble ${m.role}`}>
                  <div className="who">{m.role === "interviewer" ? "Interviewer" : "You"}</div>
                  <div>{m.text}</div>
                </div>
              ))}
              {busy && (
                <div className="bubble interviewer">
                  <div className="who">Interviewer</div>
                  <div className="muted">typing…</div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {error && <div className="error-box">{error}</div>}

            {completed ? (
              <div className="success-box" style={{ marginTop: 12 }}>
                ✅ The interview is complete. Thank you, {session.candidate_name}! The hiring
                team will review your answers and contact you about the next steps.
              </div>
            ) : (
              <form className="chat-input" onSubmit={send}>
                <textarea
                  rows={2}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send(e);
                    }
                  }}
                  placeholder="Type your answer… (Enter to send, Shift+Enter for a new line)"
                  disabled={busy}
                />
                <button className="btn" disabled={busy || !input.trim()}>Send</button>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
}
