import React, { useState, useEffect, useRef, FormEvent, ChangeEvent } from "react";
import './App.css';

type AppPhase = "url" | "name" | "chat";

const App: React.FC = () => {
  const [phase, setPhase] = useState<AppPhase>("url");
  const [serverUrl, setServerUrl] = useState<string>("");
  const [name, setName] = useState<string>("");
  const [inputValue, setInputValue] = useState<string>("");
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();

    if (phase === "url") {
      try {
        const url = new URL(inputValue);
        setServerUrl(url.toString());
        setInputValue("");
        setPhase("name");
      } catch {
        alert("URL no válida");
      }
    } else if (phase === "name") {
      setName(inputValue);
      const ws = new WebSocket(serverUrl);
      wsRef.current = ws;

      ws.onopen = (): void => {
        ws.send(inputValue);
      };
      setInputValue("");

      ws.onmessage = (event: MessageEvent<string>): void => {
        const msg: string = event.data;
        if (msg.startsWith("ERROR:")) {
          alert(msg);
          ws.close();
          wsRef.current = null;
          setPhase("name");
        } else {
          setPhase("chat");
        }
      };

      ws.onclose = (): void => {
        setMessages((prev: string[]) => [...prev, "Conexión cerrada."]);
        setPhase("name");
      };
    } else if (phase === "chat") {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(inputValue);
        setMessages((prev: string[]) => [...prev, `Tú: ${inputValue}`]);
        setInputValue("");
      }
    }
  };

  useEffect(() => {
    const ws = wsRef.current;
    if (!ws) return;

    const onMessage = (event: MessageEvent<string>): void => {
      const msg: string = event.data;
      setMessages((prev: string[]) => [...prev, msg]);
    };
  
    const handleBeforeUnload = () => {
      ws.close();
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    ws.addEventListener("message", onMessage);
    ws.onclose = (): void => {
      setMessages((prev: string[]) => [...prev, "Conexión cerrada por el servidor."]);
      wsRef.current = null;
      setPhase("url");
    };

    return () => {   
      ws.removeEventListener("message", onMessage);
      window.removeEventListener("beforeunload", handleBeforeUnload);
      ws.close();
      wsRef.current = null;
    };
  }, [phase]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    setInputValue(e.target.value);
  };

  const handleCloseConnection = (): void => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setMessages([]);
    setName("");
    setServerUrl("");
    setPhase("url");
  };

  return (
    <div id="main_div">
      {phase !== "chat" && (
        <form onSubmit={handleSubmit}>
          <input
            className="text_input"
            type="text"
            placeholder={phase === "url" ? "wss://servidor..." : "Tu nombre"}
            value={inputValue}
            onChange={handleInputChange}
            required
          />
          <button type="submit">Ingresar</button>
        </form>
      )}

      {phase === "chat" && (
        <>
          <h1>Bienvenido, {name}!</h1>
          <button id="exit_button" type="button" onClick={handleCloseConnection}>Salir</button>
          <div id="chat_div">
            {messages.map((msg: string, idx: number) => (
              <div key={idx}>{msg}</div>
            ))}
          </div>
          <form onSubmit={handleSubmit}>
            <input
              className="text_input"
              type="text"
              placeholder="Escribe un mensaje..."
              value={inputValue}
              onChange={handleInputChange}
              required
            />
            <button type="submit">Enviar</button>
          </form>
        </>
      )}
    </div>
  );
};

export default App;
