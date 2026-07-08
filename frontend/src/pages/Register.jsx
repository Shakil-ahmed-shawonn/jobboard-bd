/**
 * pages/Register.jsx
 * Role toggle (employer/seeker). Employer role reveals a required
 * `company_name` field, matching the backend's validation rule.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "seeker",
    companyName: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(" ") : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto mt-16 max-w-sm px-6">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900">Create an account</h1>

      <div className="mb-6 flex rounded-md border border-zinc-300 p-1 text-sm">
        {["seeker", "employer"].map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setForm({ ...form, role: r })}
            className={`flex-1 rounded py-1.5 capitalize transition ${
              form.role === r ? "bg-emerald-600 text-white" : "text-zinc-600"
            }`}
          >
            {r === "seeker" ? "Job seeker" : "Employer"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-zinc-700">Username</label>
          <input
            type="text"
            required
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-zinc-700">Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        {form.role === "employer" && (
          <div>
            <label className="mb-1 block text-sm text-zinc-700">Company name</label>
            <input
              type="text"
              required
              value={form.companyName}
              onChange={(e) => setForm({ ...form, companyName: e.target.value })}
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
            />
          </div>
        )}

        <div>
          <label className="mb-1 block text-sm text-zinc-700">Password</label>
          <input
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-emerald-600 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
    </div>
  );
}
