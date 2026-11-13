"""All catalog entries here are illustrative and must NEVER imply real supplier stock."""
from .schemas import ProductOut
PRODUCTS = [
    ProductOut(id="demo-headphones", name="Studio Wireless Headphones", category="Audio", price_minor=285000, currency="BDT", description="Comfortable over-ear listening with minimalist style.", in_stock=False, emoji="🎧", demo=True),
    ProductOut(id="demo-bag", name="Everyday Travel Backpack", category="Lifestyle", price_minor=420000, currency="BDT", description="Smart organization for everyday work and travel.", in_stock=False, emoji="🎒", demo=True),
    ProductOut(id="demo-lamp", name="Ambient Desk Light", category="Home", price_minor=195000, currency="BDT", description="Soft light for a calm and comfortable workspace.", in_stock=False, emoji="💡", demo=True),
    ProductOut(id="demo-watch", name="Minimal Smart Watch", category="Tech", price_minor=620000, currency="BDT", description="Thoughtful utility in a streamlined design.", in_stock=False, emoji="⌚", demo=True),
]
