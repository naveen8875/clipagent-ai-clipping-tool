import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import "./globals.css";
import { Header } from "@/components/dashboard/Header";

const defaultUrl = process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(defaultUrl),
  title: "ClipAgent - Self-Hosted AI Clipping Tool",
  description:
    "Turn long-form videos into short clips with a self-hosted AI clipping workflow.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <head />
      <body className="antialiased">
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  );
}
