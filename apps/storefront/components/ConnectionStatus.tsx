"use client";

import { useEffect, useState } from "react";

type SocketStatus = "connecting" | "connected" | "disconnected" | "disabled";
type ServerMessage = { type?: string; mode?: string };
const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";
const url = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001/ws/v1/demo";

export default function ConnectionStatus() {
  const [status, setStatus] = useState<SocketStatus>("connecting");

  useEffect(() => {
    let disposed = false;
    const controller = new AbortController();
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    let heartbeatTimer: ReturnType<typeof setInterval> | undefined;

    const connect = () => {
      if (disposed) return;
      setStatus("connecting");
      try {
        socket = new WebSocket(url);
        socket.onopen = () => {
          if (disposed) return;
          heartbeatTimer = setInterval(() => {
            if (socket?.readyState === WebSocket.OPEN) {
              socket.send(JSON.stringify({ type: "ping" }));
            }
          }, 25000);
        };
        socket.onmessage = (event: MessageEvent<string>) => {
          try {
            const data = JSON.parse(event.data) as ServerMessage;
            if (data.type === "system.connected" && data.mode === "demo") setStatus("connected");
          } catch { /* Untrusted socket payloads are never executed. */ }
        };
        socket.onerror = () => socket?.close();
        socket.onclose = () => {
          if (heartbeatTimer !== undefined) clearInterval(heartbeatTimer);
          heartbeatTimer = undefined;
          if (!disposed) {
            setStatus("disconnected");
            reconnectTimer = setTimeout(connect, 5000);
          }
        };
      } catch {
        if (!disposed) {
          setStatus("disconnected");
          reconnectTimer = setTimeout(connect, 5000);
        }
      }
    };

    fetch(api + "/api/v1/capabilities", { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error("API unavailable");
        return await response.json() as { catalog_mode: string };
      })
      .then(capabilities => {
        if (disposed) return;
        if (capabilities.catalog_mode === "demo") connect();
        else setStatus("disabled");
      })
      .catch(() => { if (!disposed && !controller.signal.aborted) setStatus("disconnected"); });

    return () => {
      disposed = true;
      controller.abort();
      if (heartbeatTimer !== undefined) clearInterval(heartbeatTimer);
      if (reconnectTimer !== undefined) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  const label =
    status === "connected" ? "Demo WebSocket connected" :
    status === "connecting" ? "Connecting demo channel…" :
    status === "disabled" ? "Private live updates not enabled" :
    "Demo WebSocket offline";

  return <div className={"realtime-indicator realtime-" + status}
    role="status" aria-live="polite" aria-label={label}
    title="Real customer order updates require an authenticated, production-grade WebSocket channel.">
    <span className="realtime-dot" aria-hidden="true" /><span>{label}</span>
  </div>;
}
