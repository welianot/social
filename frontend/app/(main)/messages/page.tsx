"use client";

import { useEffect, useState } from "react";
import { api, Conversation, Message } from "@/lib/api";
import { createClient } from "@/lib/supabase";

export default function MessagesPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    api.getConversations().then(setConversations);
  }, []);

  useEffect(() => {
    if (!active) return;
    api.getMessages(active).then((res) => setMessages(res.items));

    const supabase = createClient();
    const channel = supabase
      .channel(`messages:${active}`)
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "messages", filter: `conversation_id=eq.${active}` },
        (payload) => setMessages((prev) => [...prev, payload.new as Message])
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, [active]);

  async function send() {
    if (!active || !text.trim()) return;
    await api.sendMessage(active, text);
    setText("");
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] border rounded-xl overflow-hidden">
      <div className="w-1/3 border-r overflow-y-auto">
        <h2 className="p-4 font-semibold text-sm border-b">Messages</h2>
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => setActive(c.id)}
            className={`w-full text-left p-4 border-b hover:bg-muted/50 text-sm ${active === c.id ? "bg-muted" : ""}`}
          >
            {c.participants[0]?.display_name ?? c.participants[0]?.username ?? "Chat"}
          </button>
        ))}
      </div>
      <div className="flex-1 flex flex-col">
        {active ? (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m) => (
                <div key={m.id} className="text-sm bg-muted rounded-lg px-3 py-2 max-w-xs">
                  {m.body}
                </div>
              ))}
            </div>
            <div className="border-t p-3 flex gap-2">
              <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Message…"
                className="flex-1 border rounded-lg px-3 py-2 text-sm"
              />
              <button onClick={send} className="bg-primary text-white px-4 py-2 rounded-lg text-sm">
                Send
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
            Select a conversation
          </div>
        )}
      </div>
    </div>
  );
}
