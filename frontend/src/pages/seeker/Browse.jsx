/**
 * pages/seeker/Browse.jsx
 * Public job list with search/location filters, and an inline apply
 * form (resume upload) per job card.
 */
import { useEffect, useState } from "react";
import client from "../../api/client";

function ApplyForm({ jobId, onApplied }) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [coverNote, setCoverNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleApply(e) {
    e.preventDefault();
    if (!file) return setError("Attach a resume (.pdf or .docx) first.");
    setSubmitting(true);
    setError("");

    const formData = new FormData();
    formData.append("job", jobId);
    formData.append("resume_file", file);
    formData.append("cover_note", coverNote);

    try {
      await client.post("/applications/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onApplied();
    } catch (err) {
      const data = err.response?.data;
      setError(
        data?.non_field_errors?.[0] ||
          data?.resume_file?.[0] ||
          "Could not submit application — you may have already applied."
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mt-3 rounded-md bg-emerald-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
      >
        Apply
      </button>
    );
  }

  return (
    <form onSubmit={handleApply} className="mt-3 space-y-2 border-t border-zinc-100 pt-3">
      <input
        type="file"
        accept=".pdf,.docx"
        onChange={(e) => setFile(e.target.files[0])}
        className="text-xs"
      />
      <textarea
        placeholder="Optional cover note"
        value={coverNote}
        onChange={(e) => setCoverNote(e.target.value)}
        rows={2}
        className="w-full rounded-md border border-zinc-300 px-2 py-1 text-xs"
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="rounded-md bg-emerald-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
      >
        {submitting ? "Submitting…" : "Submit application"}
      </button>
    </form>
  );
}

export default function Browse() {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [appliedIds, setAppliedIds] = useState(new Set());
  const [expandedId, setExpandedId] = useState(null);
  const [detailsCache, setDetailsCache] = useState({});
  const [detailsLoading, setDetailsLoading] = useState(false);

  function fetchJobs() {
    client
      .get("/jobs/", { params: { search, location } })
      .then((res) => setJobs(res.data.results ?? res.data));
  }

  useEffect(() => {
    fetchJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /** Toggles the expanded detail panel; fetches full job (description +
   * requirements) on first open only, then caches it by id. */
  async function toggleDetails(jobId) {
    if (expandedId === jobId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(jobId);
    if (!detailsCache[jobId]) {
      setDetailsLoading(true);
      const { data } = await client.get(`/jobs/${jobId}/`);
      setDetailsCache((prev) => ({ ...prev, [jobId]: data }));
      setDetailsLoading(false);
    }
  }

  return (
    <div className="mx-auto mt-8 max-w-3xl px-6">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          fetchJobs();
        }}
        className="mb-6 flex gap-3"
      >
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search title or description"
          className="flex-1 rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
        />
        <input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Location"
          className="w-40 rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
        />
        <button className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800">
          Search
        </button>
      </form>

      <ul className="space-y-3">
        {jobs.map((job) => (
          <li key={job.id} className="rounded-md border border-zinc-200 p-4">
            <button
              onClick={() => toggleDetails(job.id)}
              className="text-left font-medium text-zinc-900 hover:text-emerald-700"
            >
              {job.title}
            </button>
            <p className="text-sm text-zinc-500">
              {job.company_name || "Company"} · {job.location || "Location not specified"}
              {job.salary_range && ` · ${job.salary_range}`}
            </p>

            {expandedId === job.id && (
              <div className="mt-3 border-t border-zinc-100 pt-3 text-sm text-zinc-700">
                {detailsLoading && !detailsCache[job.id] ? (
                  <p className="text-zinc-400">Loading details…</p>
                ) : (
                  <>
                    <p className="whitespace-pre-line">{detailsCache[job.id]?.description}</p>
                    <p className="mt-2 font-medium text-zinc-900">Requirements</p>
                    <p className="whitespace-pre-line">{detailsCache[job.id]?.requirements}</p>
                  </>
                )}
              </div>
            )}

            {!appliedIds.has(job.id) && (
              <ApplyForm
                jobId={job.id}
                onApplied={() => setAppliedIds(new Set(appliedIds).add(job.id))}
              />
            )}
            {appliedIds.has(job.id) && (
              <p className="mt-3 text-xs font-medium text-emerald-700">Application submitted</p>
            )}
          </li>
        ))}
        {jobs.length === 0 && <p className="text-sm text-zinc-400">No jobs match your search.</p>}
      </ul>
    </div>
  );
}
