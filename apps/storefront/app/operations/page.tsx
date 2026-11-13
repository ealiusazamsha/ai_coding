"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Activity, AlertTriangle, Bot, CheckCircle2, LockKeyhole, LogOut, Package, PackageCheck, Plus, RefreshCw, ShieldCheck, Store } from "lucide-react";
import "./operations.css";

type Summary = {
  products: number; published_products: number; suppliers: number;
  approved_suppliers: number; unverified_offers: number; pending_orders: number;
  payment_processing_enabled: boolean; supplier_purchasing_enabled: boolean;
};
type Supplier = { id: string; name: string; integration_type: string; approved: boolean };
type Product = { id: string; sku: string; name: string; description: string; category: string; status: string; sale_price_minor: number; currency: string };
type Offer = { id: string; product_id: string; supplier_id: string; supplier_sku: string; unit_cost_minor: number; currency: string; quantity: number; source_verified: boolean };
type Audit = { id: string; action: string; resource_type: string; occurred_at: string; correlation_id: string };
type Capabilities = { catalog_mode: string };

const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://bborikhazomedjzihyiv.supabase.co";
const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || "";
const money = (minor: number, currency: string) =>
  new Intl.NumberFormat("en-BD", { style: "currency", currency, maximumFractionDigits: 0 }).format(minor / 100);

async function authorized<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(api + "/api/v1/admin" + path, {
    ...init,
    cache: "no-store",
    headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === "string" ? error.detail : "Request failed (" + response.status + ")");
  }
  return response.json() as Promise<T>;
}

export default function Operations() {
  const [mode, setMode] = useState<"loading" | "demo" | "database" | "offline">("loading");
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [supplierName, setSupplierName] = useState("");
  const [supplierType, setSupplierType] = useState("manual");
  const [productSku, setProductSku] = useState("");
  const [productName, setProductName] = useState("");
  const [productPrice, setProductPrice] = useState("");
  const [offerSupplier, setOfferSupplier] = useState("");
  const [offerProduct, setOfferProduct] = useState("");
  const [offerSku, setOfferSku] = useState("");
  const [offerCost, setOfferCost] = useState("");
  const [offerQuantity, setOfferQuantity] = useState("0");

  useEffect(() => {
    const controller = new AbortController();
    fetch(api + "/api/v1/capabilities", { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error();
        return await response.json() as Capabilities;
      })
      .then(result => setMode(result.catalog_mode === "database" ? "database" : "demo"))
      .catch(() => { if (!controller.signal.aborted) setMode("offline"); });
    return () => controller.abort();
  }, []);

  async function loadData(accessToken: string) {
    const [s, su, pr, of, au] = await Promise.all([
      authorized<Summary>("/summary", accessToken),
      authorized<Supplier[]>("/suppliers", accessToken),
      authorized<Product[]>("/products", accessToken),
      authorized<Offer[]>("/offers", accessToken),
      authorized<Audit[]>("/audit?limit=20", accessToken),
    ]);
    setSummary(s); setSuppliers(su); setProducts(pr); setOffers(of); setAudit(au);
  }

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setNotice(""); setBusy(true);
    try {
      const response = await fetch(supabaseUrl + "/auth/v1/token?grant_type=password", {
        method: "POST",
        headers: { "Content-Type": "application/json", "apikey": publishableKey },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const result = await response.json();
      if (!response.ok || !result.access_token) throw new Error(result.msg || result.error_description || "Sign-in failed");
      await loadData(result.access_token);
      setToken(result.access_token);
      setPassword("");
      setNotice("Authenticated operator session. Tokens are held in memory only.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally { setBusy(false); }
  }

  async function action<T>(path: string, method: "POST" | "PATCH", data: object, message: string) {
    setError(""); setNotice(""); setBusy(true);
    try {
      await authorized<T>(path, token, { method, body: JSON.stringify(data) });
      await loadData(token);
      setNotice(message);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Operation failed";
      setError(message);
      if (message.includes("token") || message.includes("Authentication")) setToken("");
    } finally { setBusy(false); }
  }

  function logout() {
    setToken(""); setPassword(""); setSummary(null); setSuppliers([]); setProducts([]);
    setOffers([]); setAudit([]); setError(""); setNotice("Signed out from the operator console.");
  }

  const isAdmin = Boolean(token && summary);

  return <main className="ops-wrap">
    <div className="ops-top">
      <a href="/" className="brand">a<span>acp.</span></a>
      <div className="ops-header-actions">
        {isAdmin && <button className="btn secondary" onClick={logout}><LogOut size={15}/> Sign out</button>}
        <a className="btn secondary" href="/">Back to storefront</a>
      </div>
    </div>
    <span className="eyebrow">MERCHANT CONTROL CENTER</span>
    <h1>Commerce operations</h1>
    <p className="muted">Manage approved suppliers, product drafts, manual inventory records and auditable operations.</p>

    <div className="ops-warning"><AlertTriangle size={20}/>
      <span><b>Transactions locked.</b> Real payments, supplier orders, refunds and autonomous purchasing remain disabled. Manual stock entries are never supplier-verified.</span>
    </div>

    {error && <p className="ops-error" role="alert">{error}</p>}
    {notice && <p className="ops-success" role="status">{notice}</p>}

    {mode !== "database" && <section className="ops-setup">
      <div className="ops-setup-icon"><LockKeyhole size={24}/></div>
      <div><h2>{mode === "offline" ? "Backend unavailable" : mode === "loading" ? "Checking backend connection…" : "Cloud merchant operations not activated"}</h2>
        <p>The demo storefront is safe to browse. Database-backed administration requires the AACP Supabase migrations, private FastAPI configuration and an allowlisted operator account.</p>
        <p className="muted">API mode: {mode} · Existing catalog remains a development demonstration.</p>
      </div>
    </section>}

    {mode === "database" && !isAdmin && <section className="ops-setup">
      <div className="ops-setup-icon"><ShieldCheck size={27}/></div>
      <div className="ops-login">
        <h2>Sign in as a merchant operator</h2>
        <p>Use an existing Supabase Auth account explicitly included in the FastAPI operator allowlist. Self-registration is disabled in this console.</p>
        {!publishableKey
          ? <p className="ops-error">NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY must be configured when building the storefront.</p>
          : <form className="ops-form" onSubmit={signIn}>
              <label>Email <input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)}/></label>
              <label>Password <input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)}/></label>
              <button className="btn" disabled={busy}>{busy ? "Checking credentials…" : "Sign in securely"}</button>
            </form>}
        <p className="ops-caption">Credentials go directly from the browser to Supabase Auth. Access tokens remain in memory and are never saved to local storage.</p>
      </div>
    </section>}

    <div className="ops-stats">
      {[
        { label: "Catalog products", value: summary?.products ?? "—", icon: Package },
        { label: "Published listings", value: summary?.published_products ?? "—", icon: PackageCheck },
        { label: "Approved suppliers", value: summary?.approved_suppliers ?? "—", icon: Store },
        { label: "Unverified stock records", value: summary?.unverified_offers ?? "—", icon: Activity },
      ].map(item => <div className="ops-stat" key={item.label}><item.icon size={23}/><span>{item.label}</span><b>{item.value}</b></div>)}
    </div>

    {isAdmin && <div className="ops-admin-grid">
      <section className="ops-panel">
        <div className="ops-panel-head"><h2>Suppliers</h2><span>{suppliers.length} records</span></div>
        <form className="ops-form ops-inline-form" onSubmit={e => {
          e.preventDefault(); void action("/suppliers", "POST", { name: supplierName, integration_type: supplierType }, "Supplier created. Approval is off by default.");
          setSupplierName("");
        }}>
          <input required minLength={2} maxLength={160} value={supplierName} onChange={e => setSupplierName(e.target.value)} placeholder="Supplier name" aria-label="Supplier name"/>
          <select aria-label="Supplier integration type" value={supplierType} onChange={e => setSupplierType(e.target.value)}>
            <option value="manual">Manual</option><option value="file">File</option><option value="api">API</option>
          </select>
          <button className="btn" disabled={busy}><Plus size={16}/> Add supplier</button>
        </form>
        <div className="ops-list">{suppliers.length ? suppliers.map(s => <div className="ops-list-row" key={s.id}>
          <div><b>{s.name}</b><small>{s.integration_type} integration</small></div>
          <button disabled={busy} className={"ops-pill " + (s.approved ? "is-approved" : "")}
            onClick={() => void action("/suppliers/" + s.id + "/approval", "PATCH", { approved: !s.approved },
              s.approved ? "Supplier approval revoked." : "Supplier approved. Stock remains unverified until a trusted feed confirms it.")}>
            {s.approved ? "Approved" : "Approve"}
          </button>
        </div>) : <p className="muted">No supplier records yet.</p>}</div>
      </section>

      <section className="ops-panel">
        <div className="ops-panel-head"><h2>Product catalog</h2><span>{products.length} records</span></div>
        <form className="ops-form" onSubmit={e => {
          e.preventDefault();
          void action("/products", "POST", { sku: productSku, name: productName,
            sale_price_minor: Math.round(Number(productPrice) * 100), currency: "BDT" },
            "Product draft created. Publish only after reviewing the listing.");
          setProductName(""); setProductSku(""); setProductPrice("");
        }}>
          <div className="ops-form-row">
            <label>SKU <input required maxLength={128} value={productSku} onChange={e => setProductSku(e.target.value)}/></label>
            <label>Product name <input required minLength={2} value={productName} onChange={e => setProductName(e.target.value)}/></label>
          </div>
          <label>Price (BDT) <input type="number" required min="0.01" step="0.01" value={productPrice} onChange={e => setProductPrice(e.target.value)}/></label>
          <button className="btn" disabled={busy}><Plus size={16}/> Create draft</button>
        </form>
        <div className="ops-list">{products.length ? products.map(p => <div className="ops-list-row" key={p.id}>
          <div><b>{p.name}</b><small>{p.sku} · {money(p.sale_price_minor,p.currency)} · {p.status}</small></div>
          <button disabled={busy} className={"ops-pill " + (p.status === "active" ? "is-approved" : "")}
            onClick={() => void action("/products/" + p.id, "PATCH",
              { status: p.status === "active" ? "draft" : "active" },
              "Product publication state updated.")}>
            {p.status === "active" ? "Unpublish" : "Publish"}
          </button>
        </div>) : <p className="muted">No products yet.</p>}</div>
      </section>

      <section className="ops-panel">
        <div className="ops-panel-head"><h2>Manual supplier offers</h2><span>{offers.length} records</span></div>
        <p className="ops-caption">Manually entered availability is for planning only. It does not authorize fulfillment or create a verified stock indicator.</p>
        <form className="ops-form" onSubmit={e => {
          e.preventDefault();
          const product = products.find(p => p.id === offerProduct);
          void action("/offers", "POST", {
            supplier_id: offerSupplier, product_id: offerProduct,
            supplier_sku: offerSku, unit_cost_minor: Math.round(Number(offerCost)*100),
            quantity: Number(offerQuantity), currency: product?.currency || "BDT"
          }, "Unverified supplier offer recorded.");
          setOfferSku(""); setOfferCost(""); setOfferQuantity("0");
        }}>
          <div className="ops-form-row">
            <label>Supplier<select required value={offerSupplier} onChange={e => setOfferSupplier(e.target.value)}>
              <option value="">Select supplier</option>
              {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select></label>
            <label>Product<select required value={offerProduct} onChange={e => setOfferProduct(e.target.value)}>
              <option value="">Select product</option>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select></label>
          </div>
          <div className="ops-form-row">
            <label>Supplier SKU<input required value={offerSku} onChange={e => setOfferSku(e.target.value)}/></label>
            <label>Unit cost (BDT)<input type="number" min="0" step="0.01" required value={offerCost} onChange={e => setOfferCost(e.target.value)}/></label>
          </div>
          <label>Reported quantity<input type="number" min="0" step="1" required value={offerQuantity} onChange={e => setOfferQuantity(e.target.value)}/></label>
          <button className="btn" disabled={busy || !suppliers.length || !products.length}><Plus size={16}/> Record unverified offer</button>
        </form>
        <div className="ops-list">{offers.slice(0,10).map(o => <div className="ops-list-row" key={o.id}>
          <div><b>{o.supplier_sku}</b><small>{o.quantity} reported · {money(o.unit_cost_minor,o.currency)}</small></div>
          <span className={"ops-pill " + (o.source_verified ? "is-approved" : "")}>{o.source_verified ? "Verified" : "Unverified"}</span>
        </div>)}</div>
      </section>

      <section className="ops-panel">
        <div className="ops-panel-head"><h2>Audit trail</h2><button className="ops-refresh" disabled={busy} onClick={() => { setBusy(true); setError(""); void loadData(token).then(() => setNotice("Dashboard refreshed.")).catch(err => setError(err instanceof Error ? err.message : "Refresh failed")).finally(() => setBusy(false)); }}>
          <RefreshCw size={16}/> Refresh data
        </button></div>
        <div className="ops-list">{audit.length ? audit.map(item => <div className="ops-list-row" key={item.id}>
          <div><b>{item.action}</b><small>{item.resource_type} · {new Date(item.occurred_at).toLocaleString()}</small></div>
          <CheckCircle2 size={17} color="#21946a"/>
        </div>) : <p className="muted">No audited merchant actions yet.</p>}</div>
      </section>
    </div>}

    <section className="ops-panel ops-governance">
      <div className="ops-panel-head"><h2>Autonomous agent governance</h2><ShieldCheck color="#2469ec" size={24}/></div>
      <div className="ops-agents">
        {[
          { name: "Sales assistant", status: "Demo only", note: "Catalog-grounded guidance, no purchasing" },
          { name: "Supplier sourcing", status: "Not connected", note: "Requires authorized upstream supplier API" },
          { name: "Order orchestration", status: "Disabled", note: "Requires verified payment provider" },
          { name: "Customer support", status: "Not connected", note: "Requires authenticated cases and workflows" },
        ].map(a => <article className="ops-agent" key={a.name}>
          <div className="ops-agent-icon"><Bot size={22}/></div>
          <div><h3>{a.name}</h3><p>{a.note}</p></div><span>{a.status}</span>
        </article>)}
      </div>
    </section>
    <p className="ops-caption" style={{ marginTop: 26 }}>
      Operator access is controlled by verified Supabase Auth identities and the backend allowlist.
      Demo mode does not expose real merchant data. See docs/SUPABASE_SETUP.md.
    </p>
  </main>;
}
