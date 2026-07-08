/**
 * components/Navbar.jsx
 * Top nav — links change based on role. Zinc/neutral bar, single emerald
 * accent on the primary action, no decorative elements.
 */
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-lg font-semibold tracking-tight text-zinc-900">
          JobBoard <span className="text-emerald-600">BD</span>
        </Link>

        <div className="flex items-center gap-6 text-sm">
          {!user && (
            <>
              <Link to="/login" className="text-zinc-600 hover:text-zinc-900">
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
              >
                Sign up
              </Link>
            </>
          )}

          {user?.role === "employer" && (
            <>
              <Link to="/employer/post-job" className="text-zinc-600 hover:text-zinc-900">
                Post a job
              </Link>
              <Link to="/employer/dashboard" className="text-zinc-600 hover:text-zinc-900">
                Dashboard
              </Link>
            </>
          )}

          {user?.role === "seeker" && (
            <>
              <Link to="/jobs" className="text-zinc-600 hover:text-zinc-900">
                Browse jobs
              </Link>
              <Link to="/my-applications" className="text-zinc-600 hover:text-zinc-900">
                My applications
              </Link>
            </>
          )}

          {user && (
            <button onClick={handleLogout} className="text-zinc-600 hover:text-zinc-900">
              Log out
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
