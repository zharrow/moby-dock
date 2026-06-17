// Toutes les requêtes passent par /api → proxy Nginx (prod) ou Vite (dev).
const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* corps non-JSON */
    }
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  health: () => request("/health"),
  listWhales: () => request("/whales"),
  createWhale: (data) => request("/whales", { method: "POST", body: JSON.stringify(data) }),
  deleteWhale: (id) => request(`/whales/${id}`, { method: "DELETE" }),

  listContainers: () => request("/containers"),
  createContainer: (data) => request("/containers", { method: "POST", body: JSON.stringify(data) }),
  updateContainer: (id, data) =>
    request(`/containers/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  restartContainer: (id) => request(`/containers/${id}/restart`, { method: "POST" }),
  deleteContainer: (id) => request(`/containers/${id}`, { method: "DELETE" }),
};
