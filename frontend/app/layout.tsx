import type { Metadata } from "next";
import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";

import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/topbar";

import "./globals.css";

export const metadata: Metadata = {
  title: "PulseGrid — Infrastructure Monitoring",
  description: "Anomaly detection and forecasting dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body>
        <Sidebar />
        <div className="md:pl-56 lg:pl-60">
          <TopBar />
          <main className="mx-auto w-full max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
