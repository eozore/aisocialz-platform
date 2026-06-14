/**
 * Calendário visual — doc 00 §5
 *
 * O que está agendado por marca/canal, com status.
 */

export default function SchedulePage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Calendário</h2>
      <p className="text-gray-600 mb-6">
        Slots agendados por marca e canal. Cada slot tem pilar, formato e status.
      </p>

      {/* Week view placeholder */}
      <div className="grid grid-cols-7 gap-2">
        {["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"].map((day) => (
          <div key={day} className="text-center">
            <div className="text-sm font-medium text-gray-500 mb-2">{day}</div>
            <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-32 text-xs text-gray-400">
              Sem slots
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
