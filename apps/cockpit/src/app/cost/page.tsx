/**
 * Widget de custos — consome API real.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CostData {
  gasto_mes_brl: number;
  orcamento_mensal_brl: number;
  platform_status: string;
  projecao_fim_mes_brl: number;
  gatilhos: { valor: number; modo: string }[];
  top_consumidores: { agente: string; custo_brl: number }[];
}

export default function CostPage() {
  const [data, setData] = useState<CostData | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/cost`)
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch(() => {});
  }, []);

  if (!data) return <div className="text-gray-400">Carregando...</div>;

  const porcentagem = Math.round((data.gasto_mes_brl / data.orcamento_mensal_brl) * 100);
  const statusColor = data.platform_status === "ativo" ? "bg-green-500" : data.platform_status === "economia" ? "bg-yellow-500" : "bg-red-500";

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Controle de Custos</h2>

      {/* Budget bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium">R$ {data.gasto_mes_brl.toFixed(2)}</span>
          <span className="text-sm text-gray-500">R$ {data.orcamento_mensal_brl.toFixed(2)}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 relative">
          <div
            className="bg-green-500 h-4 rounded-full transition-all"
            style={{ width: `${Math.min(porcentagem, 100)}%` }}
          />
          <div className="absolute top-0 left-[33%] w-0.5 h-4 bg-yellow-500" title="R$200 — Aviso" />
          <div className="absolute top-0 left-[66%] w-0.5 h-4 bg-orange-500" title="R$400 — Economia" />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-400">
          <span>R$200 aviso</span>
          <span>R$400 economia</span>
          <span>R$600 bloqueio</span>
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Projeção fim do mês: R$ {data.projecao_fim_mes_brl.toFixed(2)}
        </div>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-3 mb-6">
        <div className={`w-3 h-3 rounded-full ${statusColor}`} />
        <span className="font-medium">Status: {data.platform_status}</span>
      </div>

      {/* Top consumidores */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-medium text-sm mb-3">Top consumidores</h3>
        <div className="space-y-2">
          {data.top_consumidores.map((c) => (
            <div key={c.agente} className="flex justify-between text-sm">
              <span className="text-gray-600">🤖 {c.agente}</span>
              <span className="font-mono text-gray-800">R$ {c.custo_brl.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
