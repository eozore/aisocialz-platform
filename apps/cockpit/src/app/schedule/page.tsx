/**
 * Calendário visual — consome API real.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Slot {
  dia: string;
  hora: string;
  canal: string;
  pilar: string;
  formato: string;
  status: string;
}

const CANAL_EMOJI: Record<string, string> = {
  linkedin: "💼",
  instagram: "📸",
  threads: "🧵",
  blog: "📝",
  youtube: "🎬",
};

export default function SchedulePage() {
  const [slots, setSlots] = useState<Slot[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/schedule`)
      .then((r) => r.json())
      .then((data) => setSlots(data.slots || []))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Calendário</h2>
      <p className="text-gray-600 mb-6">
        Slots agendados por marca e canal.
      </p>

      {slots.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
          Carregando...
        </div>
      ) : (
        <div className="space-y-2">
          {slots.map((slot, i) => (
            <div
              key={i}
              className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4"
            >
              <div className="w-24 text-sm font-mono text-gray-600">
                {slot.dia.slice(5)} {slot.hora}
              </div>
              <span className="text-lg">{CANAL_EMOJI[slot.canal] || "📌"}</span>
              <div className="flex-1">
                <span className="font-medium text-sm">{slot.formato.replace(/_/g, " ")}</span>
                <span className="text-gray-500 text-xs ml-2">• {slot.pilar}</span>
              </div>
              <span className={`text-xs px-2 py-1 rounded ${slot.status === "reservado" ? "bg-blue-50 text-blue-600" : "bg-gray-100 text-gray-500"}`}>
                {slot.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
