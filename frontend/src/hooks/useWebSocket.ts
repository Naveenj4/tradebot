import { useEffect, useState, useRef } from 'react';
import type { TelemetryState } from '../types';

export function useWebSocket() {
  const [state, setState] = useState<TelemetryState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimeout: any = null;

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'STATE_UPDATE') {
              setState(msg.data);
            }
          } catch (e) {
            console.error('WS payload error', e);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeout = setTimeout(connect, 2000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (err) {
        reconnectTimeout = setTimeout(connect, 2000);
      }
    };

    connect();

    // Secondary fallback polling every 2s
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch('/api/monitor/status');
        if (res.ok) {
          const data = await res.json();
          setState(data);
        }
      } catch (e) {
        // silently handled
      }
    }, 2000);

    return () => {
      clearTimeout(reconnectTimeout);
      clearInterval(pollInterval);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { state, isConnected };
}
