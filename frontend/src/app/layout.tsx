import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Monteiro OS",
  description: "Plataforma interna de Monteiro OS",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
