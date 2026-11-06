import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AgencIA NTM",
    template: "%s · AgencIA NTM",
  },
  description:
    "Plataforma SaaS multi-tenant para administração, configuração e comercialização de agentes de inteligência artificial.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
