/**
 * Acervo de mídia — kit de marca + categorias + dimensões.
 */
"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface MediaData {
  kit_de_marca: { cores: any[]; fontes: any[]; logos: any[] };
  categorias: { id: string; nome: string; total: number }[];
  dimensoes_disponiveis: { id: string; uso: string }[];
  assets: any[];
}

export default function MediaPage() {
  const [data, setData] = useState<MediaData | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/media`)
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch(() => {});
  }, []);

  if (!data) return <div className="text-gray-400">Carregando...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Acervo de Mídia</h2>

      {/* Kit de marca */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h3 className="font-medium text-sm mb-3">🎨 Kit de Marca</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl mb-1">🎨</div>
            <div className="text-xs text-gray-600">Cores</div>
            <div className="text-lg font-bold">{data.kit_de_marca.cores.length}</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl mb-1">🔤</div>
            <div className="text-xs text-gray-600">Fontes</div>
            <div className="text-lg font-bold">{data.kit_de_marca.fontes.length}</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl mb-1">✦</div>
            <div className="text-xs text-gray-600">Logos</div>
            <div className="text-lg font-bold">{data.kit_de_marca.logos.length}</div>
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-3">Configure cores, fontes e logos no onboarding ou aqui.</p>
      </div>

      {/* Categorias */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h3 className="font-medium text-sm mb-3">📁 Por Categoria</h3>
        <div className="grid grid-cols-4 gap-2">
          {data.categorias.map((cat) => (
            <div key={cat.id} className="text-center p-2 bg-gray-50 rounded hover:bg-orange-50 cursor-pointer transition-colors">
              <div className="text-sm font-medium">{cat.nome}</div>
              <div className="text-xs text-gray-400">{cat.total} assets</div>
            </div>
          ))}
        </div>
      </div>

      {/* Dimensões */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h3 className="font-medium text-sm mb-3">📐 Por Dimensão</h3>
        <div className="grid grid-cols-3 gap-2">
          {data.dimensoes_disponiveis.map((dim) => (
            <div key={dim.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded text-xs">
              <span className="font-mono font-medium">{dim.id}</span>
              <span className="text-gray-400">{dim.uso}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Upload */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-orange-400 transition-colors cursor-pointer">
        <p className="text-gray-500">Arraste arquivos aqui ou clique para upload</p>
        <p className="text-xs text-gray-400 mt-1">PNG, JPG, SVG, MP4 — categorizados e vetorizados automaticamente</p>
      </div>
    </div>
  );
}
