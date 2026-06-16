/**
 * Template Studio — organizado por formato + canal.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Template {
  id: string;
  nome: string;
  status: string;
  versao: string;
}

interface FormatoGroup {
  formato: string;
  canais: string[];
  dimensoes: string;
  templates: Template[];
}

const STATUS_BADGE: Record<string, string> = {
  aprovado: "bg-green-100 text-green-700",
  sandbox: "bg-yellow-100 text-yellow-700",
  aposentado: "bg-gray-100 text-gray-500",
};

export default function TemplatesPage() {
  const [formatos, setFormatos] = useState<FormatoGroup[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/templates`)
      .then((r) => r.json())
      .then((data) => setFormatos(data.formatos || []))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Template Studio</h2>
      <p className="text-gray-600 mb-6">
        Templates organizados por formato. O preview usa o mesmo render da produção.
      </p>

      {formatos.length === 0 ? (
        <div className="text-gray-400">Carregando...</div>
      ) : (
        <div className="space-y-6">
          {formatos.map((grupo) => (
            <div key={grupo.formato} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-3 mb-3">
                <h3 className="font-medium">{grupo.formato.replace(/_/g, " ")}</h3>
                <span className="text-xs font-mono text-gray-400">{grupo.dimensoes}</span>
                <div className="flex gap-1">
                  {grupo.canais.map((c) => (
                    <span key={c} className="text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {grupo.templates.map((tpl) => (
                  <div
                    key={tpl.id}
                    className="border border-gray-100 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="bg-gray-100 rounded h-24 mb-2 flex items-center justify-center text-gray-400 text-xs">
                      Preview
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{tpl.nome}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${STATUS_BADGE[tpl.status] || ""}`}>
                        {tpl.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">v{tpl.versao}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
