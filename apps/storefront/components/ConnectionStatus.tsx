"use client";

import { useEffect, useState } from "react";

type SocketStatus = "connecting" | "connected" | "disconnected";
type ServerMessage = { type?: string; mode?: string };

const url = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001/ws/v1/demo";

export default function ConnectionStatus() {
  const [status, setStatus] = useState<SocketStatus>("connecting");

  useEffect(() => {
    let disposed = false;
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
            if (data.type === "system.connected" && data.mode === "demo") {
              setStatus("connected");
            }
          } catch {
            // Never execute or interpolate untrusted event data.
          }
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

    connect();
    return () => {
      disposed = true;
      if (heartbeatTimer !== undefined) clearInterval(heartbeatTimer);
      if (reconnectTimer !== undefined) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  const label =
    status === "connected" ? "Demo WebSocket connected" :
    status === "connecting" ? "Connecting demo channel…" :
    "Demo WebSocket offline";

  return (
    <div
      className={"realtime-indicator realtime-" + status}
      role="status"
      aria-live="polite"
      aria-label={label}
      title="This is a development heartbeat, not live order updates."
    >
      <span className="realtime-dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
