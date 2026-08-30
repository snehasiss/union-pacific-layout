import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { api } from "./api";
import type { RailroadState } from "./types";
import "./styles.css";

const initialState: RailroadState = {
  profile: "mac",
  connection: { status: "disconnected", port: null, error: null, changedAt: "" },
  trackPower: "off",
  emergencyStop: false,
  commandStation: null
  ,
  locomotives: {}
};

export default function App() {
  const [state, setState] = useState(initialState);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [addressText, setAddressText] = useState("");
  const [speed, setSpeed] = useState(0);
  const [direction, setDirection] = useState<"forward" | "reverse">("forward");
  const throttleTimer = useRef<number | null>(null);

  useEffect(() => {
    api.status().then(setState).catch((error) => setMessage(error.message));
    const socket = io("/csb1");
    socket.on("state:snapshot", setState);
    socket.on("state:changed", setState);
    return () => {
      socket.disconnect();
    };
  }, []);

  async function run(action: () => Promise<unknown>) {
    setBusy(true);
    setMessage(null);
    try {
      await action();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Operation failed");
    } finally {
      setBusy(false);
    }
  }

  const connected = state.connection.status === "connected";
  const address = Number(addressText);
  const validAddress = Number.isInteger(address) && address >= 1 && address <= 10293;
  const throttleEnabled = connected && state.trackPower === "on" && validAddress;
  const locomotive = validAddress ? state.locomotives[String(address)] : undefined;
  const functions = locomotive?.functions ?? {};

  useEffect(() => {
    if (locomotive?.speed !== undefined) setSpeed(locomotive.speed);
    if (locomotive?.direction) setDirection(locomotive.direction);
  }, [locomotive?.speed, locomotive?.direction]);

  function scheduleSpeed(nextSpeed: number) {
    setSpeed(nextSpeed);
    if (!throttleEnabled) return;
    if (throttleTimer.current !== null) window.clearTimeout(throttleTimer.current);
    throttleTimer.current = window.setTimeout(() => {
      run(() => api.setThrottle(address, nextSpeed, direction));
    }, 100);
  }

  async function changeDirection(nextDirection: "forward" | "reverse") {
    if (!validAddress || nextDirection === direction) return;
    if (speed > 0 && connected) {
      await run(() => api.stopLocomotive(address, direction));
      setSpeed(0);
    }
    setDirection(nextDirection);
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Union Pacific Layout</p>
          <h1>Railroad Control</h1>
        </div>
        <span className={`connection connection--${state.connection.status}`}>
          {state.connection.status}
        </span>
      </header>

      <section className="panel status-panel" aria-label="Command station status">
        <div>
          <span className="label">Host profile</span>
          <strong>{state.profile}</strong>
        </div>
        <div>
          <span className="label">Serial device</span>
          <strong>{state.connection.port ?? "Not selected"}</strong>
        </div>
        <div>
          <span className="label">Track power</span>
          <strong>{state.trackPower.toUpperCase()}</strong>
        </div>
      </section>

      {(message ?? state.connection.error) && (
        <p className="message" role="alert">{message ?? state.connection.error}</p>
      )}

      <section className="controls" aria-label="Primary controls">
        <button
          className="emergency"
          disabled={!connected || busy}
          onClick={() => run(api.emergencyStop)}
        >
          EMERGENCY STOP
        </button>

        <div className="power-row">
          <button disabled={!connected || busy || state.trackPower === "on"} onClick={() => run(() => api.setPower("on"))}>
            Power on
          </button>
          <button disabled={!connected || busy || state.trackPower === "off"} onClick={() => run(() => api.setPower("off"))}>
            Power off
          </button>
        </div>

        <button
          className="connection-action"
          disabled={busy || state.connection.status === "connecting"}
          onClick={() => run(connected ? api.disconnect : () => api.connect())}
        >
          {connected ? "Disconnect CSB1" : "Connect CSB1"}
        </button>
      </section>

      <section className="panel throttle-panel" aria-label="Locomotive throttle">
        <div className="throttle-heading">
          <div>
            <span className="label">Locomotive</span>
            <h2>Throttle</h2>
          </div>
          <label className="address-field">
            <span>DCC address</span>
            <input
              inputMode="numeric"
              pattern="[0-9]*"
              value={addressText}
              onChange={(event) => {
                setAddressText(event.target.value.replace(/\D/g, ""));
                setSpeed(0);
              }}
              placeholder="3"
              aria-invalid={addressText !== "" && !validAddress}
            />
          </label>
        </div>

        <div className="direction-row" aria-label="Direction">
          <button className={direction === "reverse" ? "selected" : ""} disabled={!validAddress || busy} onClick={() => changeDirection("reverse")}>Reverse</button>
          <button className={direction === "forward" ? "selected" : ""} disabled={!validAddress || busy} onClick={() => changeDirection("forward")}>Forward</button>
        </div>

        <label className="speed-control">
          <span>Speed <strong>{speed}</strong></span>
          <input type="range" min="0" max="126" value={speed} disabled={!throttleEnabled || busy} onChange={(event) => scheduleSpeed(Number(event.target.value))} />
        </label>

        <button className="loco-stop" disabled={!connected || !validAddress || busy} onClick={() => run(() => api.stopLocomotive(address, direction))}>
          Stop locomotive
        </button>

        <div className="function-grid" aria-label="Locomotive functions F0 through F8">
          {Array.from({ length: 9 }, (_, number) => {
            const active = Boolean(functions[String(number)]);
            return (
              <button
                key={number}
                className={active ? "active" : ""}
                aria-pressed={active}
                disabled={!throttleEnabled || busy}
                onClick={() => run(() => api.setFunction(address, number, !active))}
              >
                <span>F{number}</span>
                <small>{number === 0 ? "Headlight" : number === 1 ? "Bell" : number === 2 ? "Horn" : "Sound"}</small>
              </button>
            );
          })}
        </div>
      </section>

      <nav className="bottom-nav" aria-label="Application sections">
        <button aria-current="page">Throttle</button>
        <button disabled>Locomotives</button>
        <button disabled>Turnouts</button>
        <button disabled>System</button>
      </nav>
    </main>
  );
}
