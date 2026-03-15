"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** メッセージの役割（API 仕様・表示の user / assistant と一致） */
enum MessageRole {
  User = "user",
  Assistant = "assistant",
}

type Message = {
  role: MessageRole;
  content: string;
};

// ブラウザでは同一オリジンの /api/chat に送り、Next.js API ルートがバックエンドへプロキシする
const CHAT_URL = "/api/chat";

export default function ChatPage() {
  // messages は会話履歴を保持する配列
  const [messages, setMessages] = useState<Message[]>([]);
  // input はユーザーの入力を保持する文字列
  const [input, setInput] = useState("");
  // isLoading はローディング中かどうかを保持するフラグ
  const [isLoading, setIsLoading] = useState(false);
  // streamingContent はストリーミング中の内容を保持する文字列
  const [streamingContent, setStreamingContent] = useState("");
  // bottomRef はスクロールのアンカーを保持する ref
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, scrollToBottom]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMessage: Message = { role: MessageRole.User, content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setStreamingContent("");

    const requestMessages: Message[] = [...messages, userMessage];

    try {
      const res = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: requestMessages }),
      });

      if (!res.ok || !res.body) {
        setStreamingContent(`Error: ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer: string = ""; // buffer for partial response
      let streamed: string = ""; // final response

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        // decoder.decode()
        // 第1引数: バイト列（Uint8Array など）
        // 第2引数 { stream: true }: 「まだ続きのチャンクが来る」ことを伝える。
        //     チャンクの境目で UTF-8 の多バイト文字が割れていても、次のチャンクで正しく繋げて decode する
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split(/\r?\n/); // 改行で分割
        buffer = lines.pop() ?? ""; // まだ処理していない文字列だけがbufferに入る

        /*
        今回の split で得られた完成した行だけを処理する
        例:
          lines = "Hello\nWor" <- Helloの部分が完成(\nがあるため)
          buffer = lines.pop() <- "Wor"がbufferに入る
          loopでは"Hello"の部分を処理する
          next loopでは"Wor"の部分を処理する
        */
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue; // data: から始まらない場合はスキップ。sseではdata: から始まる。
          const data = trimmed.slice(6).trim();
          if (data === "[DONE]") {
            // メッセージが確定したので、会話履歴に追加して、ローディングを終了する。
            setMessages((prev) => [...prev, { role: MessageRole.Assistant, content: streamed }]);
            setStreamingContent("");
            setIsLoading(false);
            return;
          }
          try {
            const parsed = JSON.parse(data) as { content?: string; error?: string };
            if (parsed.error) {
              streamed += `\n[Error: ${parsed.error}]`;
              setStreamingContent(streamed);
              setIsLoading(false);
              return;
            }
            if (typeof parsed.content === "string") {
              streamed += parsed.content;
              setStreamingContent(streamed);
            }
          } catch {
            // ignore non-JSON lines
          }
        }
      }

      if (streamed) {
        setMessages((prev) => [...prev, { role: MessageRole.Assistant, content: streamed }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: MessageRole.Assistant, content: "（応答が空でした。APIキーやネットワークを確認してください。）" },
        ]);
      }
    } catch (err) {
      const msg: string = err instanceof Error ? err.message : "Unknown";
      setMessages((prev) => [...prev, { role: MessageRole.Assistant, content: `Error: ${msg}` }]);
    } finally {
      setStreamingContent(""); // clear the buffer
      setIsLoading(false);
    }
  }, [input, isLoading, messages]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    },
    [send]
  );

  return (
    <>
      <div className="messages">
        {messages.map((m: Message, i: number) => (
          <div key={i} className={`message ${m.role}`}>
            {m.content}
          </div>
        ))}
        {isLoading && !streamingContent && (
          <div className="message loading">AI is thinking...</div>
        )}
        {streamingContent && (
          <div className="message assistant">{streamingContent}</div>
        )}
        <div className="scroll-anchor" ref={bottomRef} aria-hidden />
      </div>
      <div className="input-area">
        <div className="input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="メッセージを入力... (Enter: 送信, Shift+Enter: 改行)"
            disabled={isLoading}
            rows={1}
          />
          <button
            type="button"
            className="send-btn"
            onClick={send}
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </>
  );
}
