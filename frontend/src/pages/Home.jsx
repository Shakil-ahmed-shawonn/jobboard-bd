/**
 * pages/Home.jsx
 * Landing view: shows a simple pitch for guests, or redirects logged-in
 * users to their role's primary page.
 */
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  if (user?.role === "employer") return <Navigate to="/employer/dashboard" replace />;
  if (user?.role === "seeker") return <Navigate to="/jobs" replace />;

  return (
    <div className="mx-auto mt-24 max-w-lg px-6 text-center">
      <h1 className="text-2xl font-semibold text-zinc-900">
        Hiring in Bangladesh, matched by fit — not just keywords.
      </h1>
      <p className="mt-3 text-sm text-zinc-500">
        Employers post jobs. Seekers apply. Every application is scored
        against the job's real requirements.
      </p>
    </div>
  );
}
