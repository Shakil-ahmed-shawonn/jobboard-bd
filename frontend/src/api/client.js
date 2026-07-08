/**
 * api/client.js
 * Single axios instance for all backend calls. Attaches the access token
 * to every request, and on a 401 tries one silent refresh before failing
 * (so a 30-minute access token doesn't kick users out mid-session).
 */
import axios from "axios";

const client = axios.create({ baseURL: "/api" });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let pendingQueue = [];

function resolveQueue(error, token = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  pendingQueue = [];
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return client(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      isRefreshing = false;
      localStorage.clear();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    try {
      const { data } = await axios.post("/api/auth/token/refresh/", {
        refresh: refreshToken,
      });
      localStorage.setItem("access_token", data.access);
      resolveQueue(null, data.access);
      originalRequest.headers.Authorization = `Bearer ${data.access}`;
      return client(originalRequest);
    } catch (refreshError) {
      resolveQueue(refreshError, null);
      localStorage.clear();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default client;
