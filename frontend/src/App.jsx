import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getToken, setToken } from "./api.js";
import Layout from "./components/Layout.jsx";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Jobs from "./pages/Jobs.jsx";
import UploadCVs from "./pages/UploadCVs.jsx";
import Candidates from "./pages/Candidates.jsx";
import CandidateDetail from "./pages/CandidateDetail.jsx";
import InterviewQuestions from "./pages/InterviewQuestions.jsx";
import InterviewEvaluation from "./pages/InterviewEvaluation.jsx";
import Reports from "./pages/Reports.jsx";
import Ranking from "./pages/Ranking.jsx";

export default function App() {
  const [authed, setAuthed] = useState(Boolean(getToken()));

  useEffect(() => {
    const onLogout = () => setAuthed(false);
    window.addEventListener("recruitai:logout", onLogout);
    return () => window.removeEventListener("recruitai:logout", onLogout);
  }, []);

  const logout = () => {
    setToken(null);
    setAuthed(false);
  };

  if (!authed) {
    return <Login onLogin={() => setAuthed(true)} />;
  }

  return (
    <Layout onLogout={logout}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/upload" element={<UploadCVs />} />
        <Route path="/candidates" element={<Candidates />} />
        <Route path="/candidates/:id" element={<CandidateDetail />} />
        <Route path="/questions" element={<InterviewQuestions />} />
        <Route path="/evaluation" element={<InterviewEvaluation />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/ranking" element={<Ranking />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
