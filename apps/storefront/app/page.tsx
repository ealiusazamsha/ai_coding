"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, Bot, Check, ChevronRight, Headphones, Menu, MessageCircle, Minus, Package, Plus, Search, ShieldCheck, ShoppingBag, Sparkles, Truck, X } from "lucide-react";

type Product = { id: string; name: string; category: string; price_minor: number; currency: string; description: string; emoji: string; in_stock: boolean; demo?: boolean };
type CartItem = { product: Product; quantity: number };
type Capabilities = { catalog_mode: string; live_checkout: boolean; supplier_procurement: boolean; payment_gateway: boolean; assistant_mode: string };
const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const fallback: Product[] = [
 {id:"demo-headphones",name:"Studio Wireless Headphones",category:"Audio",price_minor:285000,currency:"BDT",description:"Comfortable over-ear listening with minimalist style.",emoji:"🎧",in_stock:false,demo:true},
 {id:"demo-bag",name:"Everyday Travel Backpack",category:"Lifestyle",price_minor:420000,currency:"BDT",description:"Smart organization for everyday work and travel.",emoji:"🎒",in_stock:false,demo:true},
 {id:"demo-lamp",name:"Ambient Desk Light",category:"Home",price_minor:195000,currency:"BDT",description:"Soft light for a calm and comfortable workspace.",emoji:"💡",in_stock:false,demo:true},
 {id:"demo-watch",name:"Minimal Smart Watch",category:"Tech",price_minor:620000,currency:"BDT",description:"Thoughtful utility in a streamlined design.",emoji:"⌚",in_stock:false,demo:true}
];
function formatPrice(minor:number,currency:string){return new Intl.NumberFormat("en-BD",{style:"currency",currency,maximumFractionDigits:0}).format(minor/100);}
export default function Home(){
 const [products,setProducts]=useState<Product[]>(fallback);
 const [caps,setCaps]=useState<Capabilities|null>(null);
 const [online,setOnline]=useState(false);
 const [search,setSearch]=useState("");
 const [category,setCategory]=useState("All");
 const [cart,setCart]=useState<CartItem[]>([]);
 const [cartOpen,setCartOpen]=useState(false);
 const [chatOpen,setChatOpen]=useState(false);
 const [question,setQuestion]=useState("");
 const [answer,setAnswer]=useState("Hello! I'm the AACP preview shopping assistant. Ask about a demo product.");
 const [chatBusy,setChatBusy]=useState(false);
 const [menuOpen,setMenuOpen]=useState(false);
 const searchInput=useRef<HTMLInputElement>(null);
 useEffect(()=>{
   const abort=new AbortController();
   Promise.all([
      fetch(`${api}/api/v1/products`,{signal:abort.signal}).then(r=>{if(!r.ok)throw new Error("Catalog unavailable");return r.json();}),
      fetch(`${api}/api/v1/capabilities`,{signal:abort.signal}).then(r=>{if(!r.ok)throw new Error("Capabilities unavailable");return r.json();})
   ]).then(([p,c])=>{setProducts(p);setCaps(c);setOnline(true);}).catch(()=>{if(!abort.signal.aborted)setOnline(false);});
   return ()=>abort.abort();
 },[]);
 const categories=useMemo(()=>["All",...Array.from(new Set(products.map(p=>p.category)))],[products]);
 const visible=useMemo(()=>products.filter(p=>(category==="All"||p.category===category) && (p.name+" "+p.description).toLowerCase().includes(search.trim().toLowerCase())),[products,category,search]);
 const count=cart.reduce((n,item)=>n+item.quantity,0);
 const total=cart.reduce((n,item)=>n+item.quantity*item.product.price_minor,0);
 const cartCurrency=cart[0]?.product.currency||"BDT";
 const add=(p:Product)=>setCart(previous=>{const found=previous.find(x=>x.product.id===p.id);return found?previous.map(x=>x.product.id===p.id?{...x,quantity:Math.min(x.quantity+1,20)}:x):[...previous,{product:p,quantity:1}];});
 const change=(id:string,step:number)=>setCart(previous=>previous.map(x=>x.product.id===id?{...x,quantity:x.quantity+step}:x).filter(x=>x.quantity>0));
 async function ask(){const q=question.trim();if(!q || chatBusy)return;setChatBusy(true);setQuestion("");try{const response=await fetch(`${api}/api/v1/assistant/${caps?.catalog_mode==="database"?"catalog":"demo"}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question:q})});if(!response.ok)throw new Error();const data=await response.json();setAnswer(data.reply);}catch{setAnswer("The preview assistant is offline. Live AI shopping and product recommendations are not activated.");}finally{setChatBusy(false);}}
 return <>
 <div className="announce"><Sparkles size={14}/> <span>Smarter shopping starts with a better experience</span></div>
 <header className="top"><div className="wrap nav">
   <a href="/" className="brand" aria-label="AACP home">a<span>acp.</span></a>
   <nav className={`links ${menuOpen?"show":""}`} aria-label="Main navigation"><a href="#products" onClick={()=>setMenuOpen(false)}>Shop collection</a><a href="#why" onClick={()=>setMenuOpen(false)}>Why AACP</a><a href="/operations" onClick={()=>setMenuOpen(false)}>Operations preview</a><a href="/account" onClick={()=>setMenuOpen(false)}>My account</a></nav>
   <div className="actions"><button className="icon-button hide-mobile" aria-label="Focus search" onClick={()=>{searchInput.current?.focus();document.getElementById("products")?.scrollIntoView({behavior:"smooth"});}}><Search size={20}/></button><button className="icon-button cart-trigger" aria-label={`Open basket, ${count} items`} onClick={()=>setCartOpen(true)}><ShoppingBag size={20}/>{count>0&&<span className="cart-count">{count}</span>}</button><button className="icon-button show-mobile" aria-label="Toggle navigation" aria-expanded={menuOpen} onClick={()=>setMenuOpen(!menuOpen)}><Menu size={22}/></button></div>
 </div></header>
 <main>
 <div className="wrap">
  <section className="hero">
    <div><span className="pill"><Sparkles size={14}/> YOUR SMARTER SHOPPING EXPERIENCE</span>
      <h1>Good finds.<br/><em>Great everyday.</em></h1>
      <p className="lead">Discover a carefully curated collection for work, home, and everything in between. Browse easily, compare thoughtfully, and enjoy a more considered way to shop.</p>
      <div className="hero-buttons"><a href="#products" className="btn">Explore collection <ArrowRight size={17}/></a><button className="btn secondary" onClick={()=>setChatOpen(true)}><MessageCircle size={18}/> Ask shopping assistant</button></div>
      <div className="hero-trust"><span><Check size={16}/> Thoughtful selections</span><span><Check size={16}/> Easy discovery</span></div>
      <div className="demo-note" role="status">Development preview · No verified inventory, payments or orders</div>
    </div>
    <div className="hero-art" role="img" aria-label="Illustrative headphones on a blue display with collection cards">
      <div className="art-ring"></div><div className="orb">🎧</div>
      <div className="float f1"><span className="float-symbol">✦</span><span><strong>New perspectives</strong><small>Modern essentials</small></span></div>
      <div className="float f2"><span className="float-symbol mint">✓</span><span><strong>Easy to explore</strong><small>Designed around you</small></span></div>
    </div>
  </section>
  <div className="benefits" id="why"><div><ShieldCheck size={22}/><span><b>Confidence first</b><small>Clear product information</small></span></div><div><Sparkles size={22}/><span><b>Smarter discovery</b><small>Guided shopping preview</small></span></div><div><Truck size={22}/><span><b>Supplier-ready</b><small>Fulfillment integration planned</small></span></div></div>
  <section id="products" className="products-section">
    <div className="section-heading"><div><span className="eyebrow">EXPLORE THE COLLECTION</span><h2>Discover something you’ll love.</h2><p className="muted">Simple choices. Everyday favorites.</p></div><label className="searchbox"><Search size={18}/><input ref={searchInput} aria-label="Search products" placeholder="Search collection..." value={search} onChange={event=>setSearch(event.target.value)}/></label></div>
    <div className="catalog-line"><div className="filters" aria-label="Filter products by category">{categories.map(c=><button key={c} className={`chip ${category===c?"active":""}`} aria-pressed={category===c} onClick={()=>setCategory(c)}>{c}</button>)}</div><span className="catalog-count">{visible.length} items</span></div>
    {!online&&<p className="catalog-alert" role="status">API connection unavailable; showing illustrative products only.</p>}
    {online && caps?.catalog_mode==="demo"&&<p className="catalog-alert" role="status">Connected to demo catalog. Supplier inventory is not verified.</p>}
    <div className="grid">{visible.map((p,i)=><article className="card" key={p.id}><div className={`product-art tone-${i%4}`} role="img" aria-label={p.name}><span>{p.emoji || "🛍️"}</span><span className="product-tag">{caps?.catalog_mode === "database" ? (p.in_stock ? "Stock verified" : "Stock unverified") : "Preview"}</span></div><div className="product-meta"><span>{p.category}</span><span>{caps?.catalog_mode === "database" ? "Catalog listing" : "Demo item"}</span></div><h3 className="product-name">{p.name}</h3><p className="product-description">{p.description}</p><div className="card-foot"><div><span className="price">{formatPrice(p.price_minor,p.currency)}</span><small>{caps?.catalog_mode === "database" ? "Checkout disabled" : "Illustrative price"}</small></div><button className="add" aria-label={`Add ${p.name} to preview basket`} onClick={()=>add(p)}><Plus size={21}/></button></div></article>)}</div>
    {visible.length===0 && <div className="empty-state"><Package size={32}/><h3>No matches found</h3><p>Try another keyword or select a different category.</p><button className="btn secondary" onClick={()=>{setSearch("");setCategory("All");}}>Clear filters</button></div>}
  </section>
  <section className="banner"><div><span className="eyebrow">THE BETTER WAY TO DISCOVER</span><h2>Your personal shopping guide, coming together.</h2><p>Preview conversational product discovery today. Secure checkout and real fulfillment will activate after provider verification.</p></div><button className="btn" onClick={()=>setChatOpen(true)}>Try assistant <ChevronRight size={18}/></button></section>
 </div></main>
 <footer className="footer"><div className="wrap footer-flex"><a className="brand" href="/">a<span>acp.</span></a><span>© 2026 AACP · Development preview · No live sales</span><a href="/operations">Operations preview</a><a href="/account">My account</a></div></footer>
 <button className="chat-fab" onClick={()=>setChatOpen(true)} aria-label="Open preview assistant"><MessageCircle size={23}/><span>Ask AACP</span></button>
 {cartOpen&&<div className="overlay" onMouseDown={e=>{if(e.target===e.currentTarget)setCartOpen(false);}}><aside className="drawer" role="dialog" aria-modal="true" aria-label="Preview basket"><div className="drawer-head"><div><small className="eyebrow">YOUR SELECTIONS</small><h2>Preview basket ({count})</h2></div><button className="icon-button" aria-label="Close basket" onClick={()=>setCartOpen(false)}><X size={21}/></button></div><div className="drawer-body">{cart.length===0?<div className="empty-state"><ShoppingBag size={38}/><h3>Your basket is empty</h3><p>Explore our demo collection and add an item.</p></div>:cart.map(item=><div key={item.product.id} className="basket-item"><div className="basket-art">{item.product.emoji}</div><div className="basket-details"><strong>{item.product.name}</strong><span>{formatPrice(item.product.price_minor,item.product.currency)}</span><div className="quantity"><button aria-label={`Remove one ${item.product.name}`} onClick={()=>change(item.product.id,-1)}><Minus size={14}/></button><b>{item.quantity}</b><button aria-label={`Add one ${item.product.name}`} onClick={()=>change(item.product.id,1)}><Plus size={14}/></button></div></div></div>)}</div><div className="drawer-bottom"><div className="summary"><span>Illustrative subtotal</span><b>{formatPrice(total,cartCurrency)}</b></div><p className="muted" style={{fontSize:12}}>Shipping, tax and customs excluded. No stock is reserved.</p><button disabled className="btn disabled" style={{width:"100%"}}>Checkout not yet available</button><p className="drawer-warning">Payment and supplier integrations must be approved before real purchases.</p></div></aside></div>}
 {chatOpen&&<div className="chat-panel" role="dialog" aria-label="Preview shopping assistant"><div className="chat-head"><div className="chat-avatar"><Bot size={23}/></div><span><strong>AACP shopping assistant</strong><small>{caps?.catalog_mode==="database"?"Catalog guided · No live AI":"Preview only · Not live AI"}</small></span><button className="icon-button" aria-label="Close assistant" onClick={()=>setChatOpen(false)}><X size={19}/></button></div><div className="chat-body"><div className="chat-bubble">{answer}</div><div className="chat-suggestions">{["Show me headphones","What is popular?","Help me find something"].map(s=><button key={s} onClick={()=>setQuestion(s)}>{s}</button>)}</div></div><form className="chat-compose" onSubmit={e=>{e.preventDefault();void ask();}}><input value={question} maxLength={500} onChange={e=>setQuestion(e.target.value)} placeholder="Ask about a preview product..." aria-label="Message preview assistant"/><button disabled={!question.trim()||chatBusy} aria-label="Send question"><ArrowRight size={20}/></button></form></div>}
 </>;
}
