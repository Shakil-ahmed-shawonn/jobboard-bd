/**
 * components/ProtectedRoute.jsx
 * Redirects to /login if not authenticated, or to "/" if the role doesn't
 * match `allowedRole` (prevents a seeker from opening an employer URL directly).
 */
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowedRole }) {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (allowedRole && user.role !== allowedRole) return <Navigate to="/" replace />;

  return children;
}
