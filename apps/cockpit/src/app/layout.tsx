import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AISocialZ Cockpit",
  description: "Cockpit do CEO — plataforma de marketing operada por IA",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col gap-2">
            <h1 className="text-xl font-bold mb-6 text-orange-600">AISocialZ</h1>
            <NavLink href="/" label="Esteira" />
            <NavLink href="/approvals" label="Aprovações" />
            <NavLink href="/schedule" label="Calendário" />
            <NavLink href="/teams" label="Times" />
            <NavLink href="/chat" label="Diretor" />
            <NavLink href="/media" label="Acervo" />
            <NavLink href="/templates" label="Templates" />
            <div className="mt-auto">
              <NavLink href="/cost" label="💰 Custos" />
            </div>
          </aside>
          {/* Main content */}
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
    >
      {label}
    </a>
  );
}
