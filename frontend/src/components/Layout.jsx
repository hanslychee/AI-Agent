import { NavLink } from "react-router-dom";
import { HUMAN_REVIEW_REMINDER } from "../api.js";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/jobs", label: "Job Descriptions" },
  { to: "/upload", label: "Upload CVs" },
  { to: "/candidates", label: "Candidate Analysis" },
  { to: "/questions", label: "Interview Questions" },
  { to: "/evaluation", label: "Interview Evaluation" },
  { to: "/reports", label: "Final Reports" },
  { to: "/ranking", label: "Candidate Ranking" },
];

export default function Layout({ children, onLogout }) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          Recruit<span>AI</span>
        </div>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="spacer" />
        <button className="logout-btn" onClick={onLogout}>
          Sign out
        </button>
      </aside>
      <main className="main">
        {children}
        <div className="ethics-banner">⚖️ {HUMAN_REVIEW_REMINDER}</div>
      </main>
    </div>
  );
}
