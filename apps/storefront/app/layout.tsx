import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AACP Commerce — Discover a better everyday",
  description: "An accessible, AI-assisted commerce storefront prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
