"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ArrowLeft, CheckCircle2, LockKeyhole, LogOut, MessageCircle, Package } from "lucide-react";
import "./account.css";

type Capabilities = { catalog_mode: string };
type Order = { order_id: string; status: string; total_minor: number; currency: string };
type Ticket = { id: string; subject: string; message: string; status: string; created_at: string };

const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";
const sbUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://bborikhazomedjzihyiv.supabase.co";
const sbKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || "";

async function accountRequest<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const result = await fetch(api + "/api/v1" + path, {
    ...init, cache: "no-store",
    headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" }
  });
  if (!result.ok) {
    const info = await result.json().catch(() => ({}));
    throw new Error(typeof info.detail === "string" ? info.detail : "Request failed (" + result.status + ")");
  }
  return result.json() as Promise<T>;
}

export default function AccountPage() {
  const [mode, setMode] = useState("loading");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [cases, setCases] = useState<Ticket[]>([]);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    fetch(api + "/api/v1/capabilities", { signal: controller.signal })
      .then(async r => { if (!r.ok) throw new Error(); return await r.json() as Capabilities; })
      .then(x => setMode(x.catalog_mode))
      .catch(() => { if (!controller.signal.aborted) setMode("offline"); });
    return () => controller.abort();
  }, []);

  async function load(t: string) {
    const [nextOrders, nextCases] = await Promise.all([
      accountRequest<Order[]>("/orders", t),
      accountRequest<Ticket[]>("/support/cases", t),
    ]);
    setOrders(nextOrders); setCases(nextCases);
  }

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      const response = await fetch(sbUrl + "/auth/v1/token?grant_type=password", {
        method: "POST",
        headers: { "Content-Type": "application/json", apikey: sbKey },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const session = await response.json();
      if (!response.ok || !session.access_token) throw new Error(session.msg || session.error_description || "Unable to sign in");
      await load(session.access_token);
      setToken(session.access_token); setPassword("");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to sign in"); }
    finally { setBusy(false); }
  }

  async function submitCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      await accountRequest<Ticket>("/support/cases", token, {
        method: "POST", body: JSON.stringify({ subject: subject.trim(), message: message.trim() })
      });
      await load(token);
      setSubject(""); setMessage("");
      setNotice("Support case created successfully.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save case"); }
    finally { setBusy(false); }
  }

  function logout() {
    setToken(""); setPassword(""); setCases([]); setOrders([]);
    setNotice("Signed out. Session token cleared from memory.");
  }

  return <main className="account-page">
    <nav className="account-nav"><a href="/" className="brand">a<span>acp.</span></a><a href="/" className="account-back"><ArrowLeft size={16}/> Storefront</a></nav>
    <div className="account-heading">
      <span className="eyebrow">YOUR SHOPPING SPACE</span>
      <h1>My account</h1>
      <p>Order information and secure customer support in one place.</p>
    </div>
    {error && <div className="account-error" role="alert">{error}</div>}
    {notice && <div className="account-notice" role="status">{notice}</div>}
    {mode !== "database" && <section className="account-panel account-intro">
      <LockKeyhole size={30} color="#2469ec"/>
      <div><h2>Account services are not activated yet</h2>
        <p>Cloud database integration is required for customer accounts, persistent orders and support records. The current storefront is a safe development preview.</p>
        <p className="muted">API mode: {mode}</p></div>
    </section>}
    {mode === "database" && !token && <section className="account-panel account-signin">
      <LockKeyhole size={28} color="#2469ec"/>
      <h2>Sign in securely</h2>
      <p>Use an existing verified Supabase Auth customer account.</p>
      {!sbKey ? <div className="account-error">Customer authentication is not configured for this build.</div>
        : <form className="account-form" onSubmit={signIn}>
          <label>Email <input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)}/></label>
          <label>Password <input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)}/></label>
          <button disabled={busy} className="btn">{busy ? "Signing in…" : "Sign in"}</button>
        </form>}
      <p className="account-small">Your credentials are sent directly to Supabase Auth, not to the AACP application server. This demo holds your session token in memory only.</p>
    </section>}
    {token && <div className="account-content">
      <div className="account-session"><span><CheckCircle2 size={18}/> Signed in</span><button onClick={logout}><LogOut size={16}/> Sign out</button></div>
      <section className="account-panel">
        <h2><Package size={20}/> My orders</h2>
        {orders.length === 0 ? <p className="muted">No orders have been created for this account. Live checkout remains disabled.</p>
          : orders.map(o => <div key={o.order_id} className="account-record">
            <div><b>Order #{o.order_id.slice(0,8)}</b><small>{o.status}</small></div>
            <strong>{new Intl.NumberFormat("en-BD",{style:"currency", currency:o.currency}).format(o.total_minor/100)}</strong>
          </div>)}
      </section>
      <section className="account-panel">
        <h2><MessageCircle size={20}/> Support cases</h2>
        <form className="account-form" onSubmit={submitCase}>
          <label>Subject<input required minLength={4} maxLength={160} value={subject} onChange={e => setSubject(e.target.value)}/></label>
          <label>How can we help?<textarea required minLength={10} maxLength={3000} rows={4} value={message} onChange={e => setMessage(e.target.value)}/></label>
          <button className="btn" disabled={busy}>{busy ? "Saving…" : "Submit support case"}</button>
        </form>
        <div className="account-records">{cases.map(item => <article className="account-record" key={item.id}>
          <div><b>{item.subject}</b><small>{new Date(item.created_at).toLocaleString()}</small><p>{item.message}</p></div>
          <span className="account-status">{item.status}</span>
        </article>)}</div>
      </section>
    </div>}
  </main>;
}
