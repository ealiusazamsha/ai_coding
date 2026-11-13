"use client";

import { useEffect, useState } from "react";
import { ArrowLeft, Package, ShieldCheck, ShoppingBag, Truck } from "lucide-react";
import { useParams } from "next/navigation";
import "./product.css";

type Product = {
  id: string; name: string; category: string; price_minor: number;
  currency: string; description: string; emoji: string; in_stock: boolean; demo: boolean;
};
type Capabilities = { catalog_mode: string; live_checkout: boolean; payment_gateway: boolean };
const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";

export default function ProductDetail() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [product, setProduct] = useState<Product | null>(null);
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    Promise.all([
      fetch(api + "/api/v1/products/" + encodeURIComponent(id), { signal: controller.signal }).then(async response => {
        if (!response.ok) throw new Error(response.status === 404 ? "Product not found" : "Catalog is unavailable");
        return await response.json() as Product;
      }),
      fetch(api + "/api/v1/capabilities", { signal: controller.signal }).then(async response => {
        if (!response.ok) throw new Error("Cannot verify commerce capabilities");
        return await response.json() as Capabilities;
      })
    ]).then(([p,c]) => { setProduct(p); setCaps(c); })
      .catch(err => { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : "Request failed"); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [id]);

  const demo = caps?.catalog_mode !== "database";
  return <main className="detail-page">
    <nav className="detail-nav"><a href="/" className="brand">a<span>acp.</span></a><a href="/#products" className="detail-back"><ArrowLeft size={17}/> Back to products</a></nav>
    {loading ? <section className="detail-loading">Loading catalog details…</section>
      : error ? <section className="detail-loading" role="alert">{error} · <a href="/">Return to collection</a></section>
      : product && <div className="detail-layout">
        <div className="detail-art" role="img" aria-label={product.name}><span>{product.emoji || "🛍️"}</span></div>
        <section className="detail-info">
          <span className="eyebrow">{product.category.toUpperCase()}</span>
          <h1>{product.name}</h1>
          <div className="detail-price">{new Intl.NumberFormat("en-BD", { style: "currency", currency: product.currency, maximumFractionDigits: 0 }).format(product.price_minor / 100)}</div>
          <p className="detail-desc">{product.description || "Detailed product information will appear after supplier approval."}</p>
          <div className="detail-state">
            <ShieldCheck size={18}/>
            {demo ? "Development sample — stock and price are illustrative"
              : product.in_stock ? "Recent supplier stock has been verified"
              : "Supplier stock is not verified"}
          </div>
          <button className="btn detail-buy" disabled><ShoppingBag size={19}/> Checkout unavailable</button>
          <p className="detail-disclaimer">No payment, reservation or supplier purchase can be completed on this page. Tax, delivery and return policies require provider validation.</p>
          <div className="detail-benefits">
            <div><Package size={20}/><span>Verified descriptions planned</span></div>
            <div><Truck size={20}/><span>Shipping provider integration pending</span></div>
          </div>
        </section>
      </div>}
  </main>;
}
