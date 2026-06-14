/**
 * Template Studio — doc 07 §3
 *
 * V1: Galeria por marca + preview real.
 * Edição por código e chat = Fase 2.
 */

export default function TemplatesPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Template Studio</h2>
      <p className="text-gray-600 mb-6">
        Galeria de templates por marca. O preview usa o mesmo render da produção — pixel-perfect.
      </p>

      {/* Template cards placeholder */}
      <div className="grid grid-cols-3 gap-4">
        {["carrossel_educativo", "card_noticia", "base_tipografico"].map((tpl) => (
          <div
            key={tpl}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
          >
            <div className="bg-gray-100 rounded h-40 mb-3 flex items-center justify-center text-gray-400 text-sm">
              Preview
            </div>
            <h3 className="font-medium text-sm">{tpl.replace(/_/g, " ")}</h3>
            <span className="text-xs text-green-600">aprovado</span>
          </div>
        ))}
      </div>
    </div>
  );
}
