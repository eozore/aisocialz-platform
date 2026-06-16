/**
 * Esteira de produção — doc 09 §5
 * Consome dados reais da API.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BacklogItem {
  id: string;
  tipo: string;
  pilar: string;
  funil: string;
  status: string;
  agente_atual: string | null;
  canal: string;
}

const STATUS_COLORS: Record<string, string> = {
  ideia: "bg-gray-100 text-gray-700",
  briefing: "bg-blue-100 text-blue-700",
  producao: "bg-yellow-100 text-yellow-700",
  revisao: "bg-purple-100 text-purple-700",
  aguardando_ceo: "bg-orange-100 text-orange-700",
  aprovado: "bg-green-100 text-green-700",
  agendado: "bg-indigo-100 text-indigo-700",
  publicado: "bg-emerald-100 text-emerald-700",
};

export default function EsteiraPage() {
  const [items, setItems] = useState<BacklogItem[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/backlog`)
      .then((r) => r.json())
      .then((data) => setItems(data.items || []))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Esteira de Produção</h2>
      <p className="text-gray-600 mb-6">
        Pipeline ao vivo — cada item mostra em que etapa está e qual agente o segura.
      </p>

      {items.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
          Carregando...
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4"
            >
              <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[item.status] || "bg-gray-100"}`}>
                {item.status}
              </span>
              <div className="flex-1">
                <span className="font-medium text-sm">{item.tipo.replace(/_/g, " ")}</span>
                <span className="text-gray-500 text-xs ml-2">• {item.pilar}</span>
              </div>
              <span className="text-xs text-gray-400">{item.canal}</span>
              {item.agente_atual && (
                <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">
                  🤖 {item.agente_atual}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
