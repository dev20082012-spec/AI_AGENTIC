/**
 * Returns the API base URL.
 * - Local dev: reads VITE_API_URL from the .env file (e.g. "http://localhost:8000")
 * - Production: VITE_API_URL is empty string, so all calls use relative paths
 *   (same origin as the FastAPI server that serves this built frontend)
 */
const raw = import.meta.env.VITE_API_URL;
export const API_BASE = raw && raw.trim() !== "" ? raw.trim().replace(/\/$/, "") : "";
