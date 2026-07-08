/**
 * pages/seeker/MyApplications.jsx
 * Read-only list of the seeker's own applications, with status and
 * (if scored) the AI fit summary — lets the seeker see how they were assessed.
 */
import { useEffect, useState } from "react";
import client from "../../api/client";

const STATUS_STYLES = {
  pending: "bg-zinc-100 text-zinc-600",
  reviewed: "bg-amber-100 text-amber-700",
  shortlisted: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
};

export default function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/applications/").then((res) => {
      setApplications(res.data.results ?? res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="p-6 text-sm text-zinc-500">Loading…</p>;

  return (
    <div className="mx-auto mt-8 max-w-2xl px-6">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900">My applications</h1>

      <ul className="space-y-3">
        {applications.map((app) => (
          <li key={app.id} className="rounded-md border border-zinc-200 p-4">
            <div className="flex items-center justify-between">
              <p className="font-medium text-zinc-900">{app.job_title}</p>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${STATUS_STYLES[app.status]}`}>
                {app.status}
              </span>
            </div>
            {app.ai_fit_score != null && (
              <p className="mt-1 text-sm text-zinc-600">
                Fit score: <span className="font-medium">{app.ai_fit_score}%</span> — {app.ai_summary}
              </p>
            )}
          </li>
        ))}
        {applications.length === 0 && (
          <p className="text-sm text-zinc-400">You haven't applied to any jobs yet.</p>
        )}
      </ul>
    </div>
  );
}
