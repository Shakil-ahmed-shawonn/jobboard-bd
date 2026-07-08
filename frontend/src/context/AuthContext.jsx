/**
 * context/AuthContext.jsx
 * Holds the logged-in user's role + username (decoded from what the
 * register/login calls return) and exposes login/register/logout.
 * Tokens live in localStorage (read by api/client.js on every request).
 */
import { createContext, useContext, useState } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  /** Registers a new account, then logs in immediately. */
  async function register({ username, email, password, role, companyName }) {
    await client.post("/accounts/register/", {
      username,
      email,
      password,
      role,
      company_name: companyName || "",
    });
    await login({ username, password });
  }

  /** Logs in, stores tokens, fetches the true role from /me, updates context state. */
  async function login({ username, password }) {
    const { data } = await client.post("/auth/token/", { username, password });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);

    const { data: me } = await client.get("/accounts/me/");
    const userInfo = { username: me.username, role: me.role };
    localStorage.setItem("user", JSON.stringify(userInfo));
    setUser(userInfo);
  }

  function logout() {
    localStorage.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
