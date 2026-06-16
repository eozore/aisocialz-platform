/**
 * Chat com o Diretor — doc 09 §5
 *
 * Canal de chat onde o CEO fala em linguagem de negócio
 * e o Diretor aconselha, explica decisões e recebe diretrizes.
 */
"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Olá! Sou seu Diretor de Marketing. Posso te ajudar com estratégia, explicar decisões da equipe, ou receber novas diretrizes. Em que posso ajudar?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    // Placeholder de loading
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "Pensando...", loading: true },
    ]);

    try {
      const res = await fetch(`${API_URL}/api/chat/diretor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: userMessage }),
      });
      const data = await res.json();

      setMessages((prev) => {
        const withoutLoading = prev.filter((m) => !m.loading);
        return [...withoutLoading, { role: "assistant", content: data.resposta }];
      });
    } catch (error) {
      setMessages((prev) => {
        const withoutLoading = prev.filter((m) => !m.loading);
        return [
          ...withoutLoading,
          { role: "assistant", content: "Erro ao conectar com o Diretor. Tente novamente." },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-2xl font-bold mb-4">Conversa com o Diretor</h2>

      {/* Messages */}
      <div className="flex-1 overflow-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-2xl p-4 rounded-lg ${
              msg.role === "user"
                ? "bg-orange-50 ml-auto border border-orange-200"
                : "bg-white border border-gray-200"
            } ${msg.loading ? "animate-pulse" : ""}`}
          >
            <div className="text-xs text-gray-500 mb-1">
              {msg.role === "user" ? "Você (CEO)" : "Diretor de Marketing"}
            </div>
            <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Fale com seu Diretor de Marketing..."
          disabled={isLoading}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors disabled:opacity-50"
        >
          {isLoading ? "..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}
