/**
 * Widget de custos — doc 05 §5
 *
 * Gasto do mês vs orçamento, barra com os três gatilhos,
 * projeção de fim de mês, top 5 consumidores.
 */

export default function CostPage() {
  // Dados mockados para V1 (virão do /api/cost)
  const gasto = 0;
  const orcamento = 600;
  const porcentagem = Math.round((gasto / orcamento) * 100);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Controle de Custos</h2>
      <p className="text-gray-600 mb-6">
        Gasto do mês vs orçamento. Modo vigente sempre visível.
      </p>

      {/* Budget bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium">R$ {gasto.toFixed(2)}</span>
          <span className="text-sm text-gray-500">R$ {orcamento.toFixed(2)}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 relative">
          <div
            className="bg-green-500 h-4 rounded-full transition-all"
            style={{ width: `${porcentagem}%` }}
          />
          {/* Threshold markers */}
          <div className="absolute top-0 left-[33%] w-px h-4 bg-yellow-500" title="R$200 — Aviso" />
          <div className="absolute top-0 left-[66%] w-px h-4 bg-orange-500" title="R$400 — Economia" />
          <div className="absolute top-0 left-[100%] w-px h-4 bg-red-500" title="R$600 — Bloqueado" />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-400">
          <span>R$200 aviso</span>
          <span>R$400 economia</span>
          <span>R$600 bloqueio</span>
        </div>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-3">
        <div className="w-3 h-3 rounded-full bg-green-500" />
        <span className="font-medium">Status: Ativo</span>
        <span className="text-sm text-gray-500 ml-auto">
          Custos de build não contam para os gatilhos
        </span>
      </div>
    </div>
  );
}
