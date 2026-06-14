/**
 * Acervo de mídia — doc 10 §4
 *
 * V1 mínima: upload manual + visualização do que agentes adicionaram.
 * Busca e tags visíveis.
 */

export default function MediaPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Acervo de Mídia</h2>
      <p className="text-gray-600 mb-6">
        Imagens, vídeos e logos disponíveis para os agentes. Upload manual ou adicionados automaticamente.
      </p>

      {/* Upload area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6 hover:border-orange-400 transition-colors cursor-pointer">
        <p className="text-gray-500">Arraste arquivos aqui ou clique para upload</p>
        <p className="text-xs text-gray-400 mt-1">PNG, JPG, MP4 — serão vetorizados automaticamente</p>
      </div>

      {/* Grid placeholder */}
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
        <p>Acervo vazio. Suba seus primeiros assets.</p>
      </div>
    </div>
  );
}
