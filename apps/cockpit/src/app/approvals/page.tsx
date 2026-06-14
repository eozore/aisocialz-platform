/**
 * Fila de aprovações — doc 00 §5
 *
 * Roteiros a 4 mãos + itens approve_required + decisões estratégicas.
 * Ações: aprovar / editar via chat / rejeitar com motivo.
 */

export default function ApprovalsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Fila de Aprovações</h2>
      <p className="text-gray-600 mb-6">
        Itens que precisam da sua decisão. Motivo de rejeição alimenta o decision log.
      </p>

      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
        <p>Nenhuma aprovação pendente.</p>
        <p className="text-sm mt-2">
          Quando houver itens pendentes, eles aparecerão aqui com preview e ações.
        </p>
      </div>
    </div>
  );
}
