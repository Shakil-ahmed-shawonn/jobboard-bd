/**
 * pages/employer/PostJob.jsx
 * Form to create a JobPost. `requirements` is the field sent to Claude
 * for resume fit-scoring, so its help text nudges the employer to be
 * specific (concrete skills, not vague adjectives).
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../../api/client";

export default function PostJob() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    description: "",
    requirements: "",
    location: "",
    salary_range: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await client.post("/jobs/", form);
      navigate("/employer/dashboard");
    } catch (err) {
      setError("Could not post the job. Check the fields and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto mt-12 max-w-2xl px-6">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900">Post a job</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-zinc-700">Job title</label>
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm text-zinc-700">Location</label>
            <input
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              placeholder="Dhaka / Remote"
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-700">Salary range</label>
            <input
              value={form.salary_range}
              onChange={(e) => setForm({ ...form, salary_range: e.target.value })}
              placeholder="৳50k - ৳80k"
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm text-zinc-700">Description</label>
          <textarea
            required
            rows={5}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-zinc-700">
            Requirements
            <span className="ml-1 font-normal text-zinc-400">
              — specific skills, tools, years of experience (this is what resumes are scored against)
            </span>
          </label>
          <textarea
            required
            rows={4}
            value={form.requirements}
            onChange={(e) => setForm({ ...form, requirements: e.target.value })}
            placeholder="e.g. Python, Django REST Framework, PostgreSQL, 2+ years backend experience"
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-emerald-600 px-5 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading ? "Posting…" : "Post job"}
        </button>
      </form>
    </div>
  );
}
