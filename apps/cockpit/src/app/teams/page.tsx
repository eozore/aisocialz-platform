/**
 * Sala de contratação — doc 09 §3
 *
 * Times como módulos contratáveis. Ativar/desativar sem quebrar nada.
 */

const TEAMS = [
  { id: "core", nome: "Core (Diretor, Estrategista, Revisor, Analista)", obrigatorio: true, ativo: true },
  { id: "linkedin", nome: "LinkedIn", obrigatorio: false, ativo: true },
  { id: "meta", nome: "Meta (Instagram + Facebook + Threads)", obrigatorio: false, ativo: true },
  { id: "blog", nome: "Blog", obrigatorio: false, ativo: true },
  { id: "radar", nome: "Radar (Contexto)", obrigatorio: false, ativo: true },
  { id: "comunidade", nome: "Comunidade", obrigatorio: false, ativo: true },
  { id: "analytics_web", nome: "Google Analytics", obrigatorio: false, ativo: true },
  { id: "youtube", nome: "YouTube", obrigatorio: false, ativo: false },
  { id: "tiktok", nome: "TikTok", obrigatorio: false, ativo: false },
  { id: "email", nome: "Email / Newsletter", obrigatorio: false, ativo: false },
];

export default function TeamsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Times Contratados</h2>
      <p className="text-gray-600 mb-6">
        Ative/desative módulos. Um time inativo não gera slots, não aparece, não consome.
      </p>

      <div className="space-y-3">
        {TEAMS.map((team) => (
          <div
            key={team.id}
            className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4"
          >
            <div>
              <span className="font-medium">{team.nome}</span>
              {team.obrigatorio && (
                <span className="ml-2 text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">
                  obrigatório
                </span>
              )}
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                defaultChecked={team.ativo}
                disabled={team.obrigatorio}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500 peer-disabled:opacity-50" />
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
