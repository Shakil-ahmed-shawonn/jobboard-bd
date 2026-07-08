/**
 * pages/employer/Dashboard.jsx
 * Left: employer's own job posts. Right: applicants to the selected job,
 * already ordered by ai_fit_score (backend default ordering) — highest
 * fit first. Status can be updated inline.
 */
import { useEffect, useState } from "react";
import client from "../../api/client";

function ScoreBadge({ score }) {
  if (score == null) {
    return <span className="text-xs text-zinc-400">Not scored</span>;
  }
  const tone =
    score >= 75 ? "bg-emerald-100 text-emerald-700" :
    score >= 50 ? "bg-amber-100 text-amber-700" :
    "bg-zinc-100 text-zinc-600";
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${tone}`}>
      {score}% fit
    </span>
  );
}

export default function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/jobs/?mine=true").then((res) => {
      setJobs(res.data.results ?? res.data);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (!selectedJob) return;
    client.get("/applications/").then((res) => {
      const all = res.data.results ?? res.data;
      setApplicants(all.filter((a) => a.job === selectedJob.id));
    });
  }, [selectedJob]);

  async function updateStatus(applicationId, status) {
    await client.patch(`/applications/${applicationId}/`, { status });
    setApplicants((prev) =>
      prev.map((a) => (a.id === applicationId ? { ...a, status } : a))
    );
  }

  if (loading) return <p className="p-6 text-sm text-zinc-500">Loading…</p>;

  return (
    <div className="mx-auto mt-8 grid max-w-5xl grid-cols-3 gap-6 px-6">
      <div className="col-span-1">
        <h2 className="mb-3 text-sm font-medium text-zinc-500">Your job posts</h2>
        <ul className="space-y-2">
          {jobs.map((job) => (
            <li key={job.id}>
              <button
                onClick={() => setSelectedJob(job)}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm transition ${
                  selectedJob?.id === job.id
                    ? "border-emerald-500 bg-emerald-50"
                    : "border-zinc-200 hover:border-zinc-300"
                }`}
              >
                <p className="font-medium text-zinc-900">{job.title}</p>
                <p className="text-xs text-zinc-500">{job.location || "No location set"}</p>
              </button>
            </li>
          ))}
          {jobs.length === 0 && (
            <p className="text-sm text-zinc-400">No job posts yet.</p>
          )}
        </ul>
      </div>

      <div className="col-span-2">
        <h2 className="mb-3 text-sm font-medium text-zinc-500">
          {selectedJob ? `Applicants — ${selectedJob.title}` : "Select a job to view applicants"}
        </h2>

        <ul className="space-y-3">
          {applicants.map((app) => (
            <li key={app.id} className="rounded-md border border-zinc-200 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-zinc-900">{app.seeker_username}</p>
                  <p className="mt-1 text-sm text-zinc-600">{app.ai_summary || "No AI summary available."}</p>
                </div>
                <ScoreBadge score={app.ai_fit_score} />
              </div>

              {app.ai_matched_skills?.length > 0 && (
                <p className="mt-2 text-xs text-zinc-500">
                  Matched: {app.ai_matched_skills.join(", ")}
                </p>
              )}
              {app.ai_missing_skills?.length > 0 && (
                <p className="text-xs text-zinc-500">
                  Missing: {app.ai_missing_skills.join(", ")}
                </p>
              )}

              <div className="mt-3 flex items-center gap-3">
                <a
                  href={app.resume_file}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-medium text-emerald-700 hover:underline"
                >
                  View resume
                </a>
                <select
                  value={app.status}
                  onChange={(e) => updateStatus(app.id, e.target.value)}
                  className="rounded-md border border-zinc-300 px-2 py-1 text-xs"
                >
                  <option value="pending">Pending</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="shortlisted">Shortlisted</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </li>
          ))}
          {selectedJob && applicants.length === 0 && (
            <p className="text-sm text-zinc-400">No applicants yet.</p>
          )}
        </ul>
      </div>
    </div>
  );
}
