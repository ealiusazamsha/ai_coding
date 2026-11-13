# Media design, assets and storage

## Repository
`apps/storefront/public/media/`: licensed public marketing imagery and optimized, immutable product placeholders.
`media/source/`: local design input only (ignored in git; may contain sensitive or third-party licensed files).
`media/optimized/`: reviewed optimized AVIF/WebP exports with metadata/alt text.
`packages/design-tokens/`: brand typography, colors and spacing.

## Supabase Storage (production)
Public product images bucket: `aacp-public`, with validated license/owner, CDN-optimized derivatives and immutable file IDs.
Private documents bucket: `aacp-private`, with authenticated authorization and short-lived signed access only.
Suggested object key: `tenants/{tenant_id}/products/{product_id}/{asset_id}.webp`. Private documents under `tenants/{tenant_id}/support/{case_id}/{asset_id}`.

## Upload security
Validate MIME bytes, sizes, aspect ratio; strip EXIF; malware scan; authorize owner and tenant; avoid using client-supplied path as proof of ownership. Public assets must never contain customer addresses, receipts, private invoices or API keys. Record rights, checksum, alt text, origin and moderation status. Do not commit fonts without redistribution rights.
