/**
 * Esteira de produção — doc 09 §5
 *
 * Cada item do backlog mostra em que etapa está e qual agente o segura.
 * Transparência vira confiança.
 */

export default function EsteiraPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Esteira de Produção</h2>
      <p className="text-gray-600 mb-6">
        Pipeline ao vivo — cada item mostra em que etapa está e qual agente o segura.
      </p>

      {/* Status badges */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {["ideia", "briefing", "producao", "revisao", "aguardando_ceo", "aprovado", "agendado", "publicado"].map((status) => (
          <span
            key={status}
            className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs font-medium text-gray-600"
          >
            {status.replace("_", " ")}
          </span>
        ))}
      </div>

      {/* Placeholder for backlog items */}
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
        <p>Nenhum item no backlog ainda.</p>
        <p className="text-sm mt-2">
          Itens aparecerão aqui quando os agentes começarem a produzir.
        </p>
      </div>
    </div>
  );
}
