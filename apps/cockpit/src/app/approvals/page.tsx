/**
 * Fila de aprovações — consome API real.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Approval {
  id: string;
  tipo: string;
  resumo: string;
  prazo: string;
  fallback: string;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/approvals`)
      .then((r) => r.json())
      .then((data) => setApprovals(data.approvals || []))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Fila de Aprovações</h2>
      <p className="text-gray-600 mb-6">
        Itens que precisam da sua decisão.
      </p>

      {approvals.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
          Nenhuma aprovação pendente.
        </div>
      ) : (
        <div className="space-y-3">
          {approvals.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg border border-gray-200 p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">
                  {item.tipo}
                </span>
                <span className="text-xs text-gray-400">prazo: {item.prazo}</span>
              </div>
              <p className="text-sm mb-3">{item.resumo}</p>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 bg-green-500 text-white text-xs rounded-md hover:bg-green-600">
                  ✓ Aprovar
                </button>
                <button className="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs rounded-md hover:bg-gray-300">
                  ✏️ Editar
                </button>
                <button className="px-3 py-1.5 bg-red-100 text-red-700 text-xs rounded-md hover:bg-red-200">
                  ✗ Rejeitar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
