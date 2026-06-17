import { useEffect, useMemo, useState } from "react";
import { api } from "./api";

const STATUSES = ["running", "stopped", "exited"];
const EMPTY_FORM = { name: "", image: "nginx:latest", status: "running", whale_id: "" };

export default function App() {
  const [health, setHealth] = useState("...");
  const [whales, setWhales] = useState([]);
  const [containers, setContainers] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const [w, c] = await Promise.all([api.listWhales(), api.listContainers()]);
      setWhales(w);
      setContainers(c);
      if (!form.whale_id && w.length) setForm((f) => ({ ...f, whale_id: w[0].id }));
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    api.health().then((h) => setHealth(h.status)).catch(() => setHealth("down"));
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Conteneurs regroupés par baleine
  const byWhale = useMemo(() => {
    const map = new Map(whales.map((w) => [w.id, []]));
    for (const c of containers) {
      if (map.has(c.whale_id)) map.get(c.whale_id).push(c);
    }
    return map;
  }, [whales, containers]);

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await api.createContainer({ ...form, whale_id: Number(form.whale_id) });
      setForm((f) => ({ ...EMPTY_FORM, whale_id: f.whale_id }));
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function cycleStatus(c) {
    const next = STATUSES[(STATUSES.indexOf(c.status) + 1) % STATUSES.length];
    try {
      await api.updateContainer(c.id, { status: next });
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function restart(c) {
    try {
      await api.restartContainer(c.id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(c) {
    try {
      await api.deleteContainer(c.id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <header className="app">
        <h1>🐳 Moby Dock</h1>
        <span className="sub">le port de conteneurs</span>
        <span className={`health ${health === "ok" ? "ok" : "down"}`}>
          API&nbsp;: {health === "ok" ? "● en ligne" : "○ injoignable"}
        </span>
      </header>

      {error && <div className="error">⚠️ {error}</div>}

      <div className="grid">
        {whales.map((whale) => (
          <section className="card" key={whale.id}>
            <div className="whale-title">
              <span>{whale.emoji}</span>
              <span>{whale.name}</span>
              <span className="count">
                — {byWhale.get(whale.id)?.length ?? 0} conteneur(s)
              </span>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Conteneur</th>
                  <th>Image</th>
                  <th>Statut</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {(byWhale.get(whale.id) ?? []).map((c) => (
                  <tr key={c.id}>
                    <td>{c.name}</td>
                    <td><code>{c.image}</code></td>
                    <td>
                      <button
                        className={`badge ${c.status}`}
                        title="Cliquer pour changer de statut"
                        onClick={() => cycleStatus(c)}
                      >
                        {c.status}
                      </button>
                    </td>
                    <td>
                      <div className="actions" style={{ justifyContent: "flex-end" }}>
                        <button className="row-btn" onClick={() => restart(c)}>↻ restart</button>
                        <button className="row-btn danger" onClick={() => remove(c)}>🗑</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {(byWhale.get(whale.id) ?? []).length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ color: "var(--muted)" }}>
                      Aucun conteneur à bord.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </section>
        ))}
      </div>

      <section className="card" style={{ marginTop: "1rem" }}>
        <div className="whale-title">➕ Lancer un conteneur</div>
        <form className="new" onSubmit={handleCreate}>
          <div>
            <label>Nom</label>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="ex. worker"
              required
            />
          </div>
          <div>
            <label>Image</label>
            <input
              value={form.image}
              onChange={(e) => setForm({ ...form, image: e.target.value })}
              placeholder="ex. postgres:16-alpine"
            />
          </div>
          <div>
            <label>Statut</label>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label>Baleine</label>
            <select
              value={form.whale_id}
              onChange={(e) => setForm({ ...form, whale_id: e.target.value })}
              required
            >
              {whales.map((w) => (
                <option key={w.id} value={w.id}>{w.emoji} {w.name}</option>
              ))}
            </select>
          </div>
          <button className="primary" type="submit">Lancer 🚀</button>
        </form>
      </section>

      <footer className="app">
        TP CI/CD — FastAPI · React · PostgreSQL · Docker Compose · GitHub Actions
      </footer>
    </div>
  );
}
