import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { api } from "./api";
import type { RailroadState, RosterLocomotive } from "./types";
import "./styles.css";

const initialState: RailroadState = {
  profile: "mac",
  connection: { status: "disconnected", port: null, error: null, changedAt: "" },
  trackPower: "off",
  emergencyStop: false,
  commandStation: null,
  locomotives: {}
};

export default function App() {
  const [state, setState] = useState(initialState);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [addressText, setAddressText] = useState("");
  const [speed, setSpeed] = useState(0);
  const [direction, setDirection] = useState<"forward" | "reverse">("forward");
  const [roster, setRoster] = useState<RosterLocomotive[]>([]);
  const [rosterError, setRosterError] = useState<string | null>(null);
  const [selectedRosterId, setSelectedRosterId] = useState("");
  const [rosterOpen, setRosterOpen] = useState(false);
  const [functionBank, setFunctionBank] = useState<0 | 1>(0);
  const [pendingFunctions, setPendingFunctions] = useState<Set<number>>(new Set());
  const throttleTimer = useRef<number | null>(null);

  useEffect(() => {
    api.status().then(setState).catch((error) => setMessage(error.message));
    const loadRoster = () => {
      api.locomotives()
        .then((result) => {
          setRoster(result.locomotives);
          setRosterError(null);
        })
        .catch(() => setRosterError("Active roster unavailable; decoder override remains available."));
    };
    loadRoster();
    const refreshTimer = window.setInterval(loadRoster, 30_000);
    window.addEventListener("focus", loadRoster);
    const socket = io("/csb1");
    socket.on("state:snapshot", setState);
    socket.on("state:changed", setState);
    return () => {
      window.clearInterval(refreshTimer);
      window.removeEventListener("focus", loadRoster);
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (roster.length === 1 && !selectedRosterId && !addressText) {
      setSelectedRosterId(roster[0].id);
      setAddressText(String(roster[0].address));
    } else if (selectedRosterId && !roster.some((item) => item.id === selectedRosterId)) {
      setSelectedRosterId("");
      setAddressText("");
      setSpeed(0);
    }
  }, [roster, selectedRosterId, addressText]);

  async function run(action: () => Promise<unknown>, blockInterface = true) {
    if (blockInterface) setBusy(true);
    setMessage(null);
    try {
      await action();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Operation failed");
    } finally {
      if (blockInterface) setBusy(false);
    }
  }

  const connected = state.connection.status === "connected";
  const address = Number(addressText);
  const validAddress = Number.isInteger(address) && address >= 1 && address <= 10293;
  const throttleEnabled = connected && state.trackPower === "on" && validAddress;
  const locomotive = validAddress ? state.locomotives[String(address)] : undefined;
  const functions = locomotive?.functions ?? {};
  const selectedRoster = roster.find((item) => item.id === selectedRosterId);
  const functionStart = functionBank * 16;

  useEffect(() => {
    if (locomotive?.speed !== undefined) setSpeed(locomotive.speed);
    if (locomotive?.direction) setDirection(locomotive.direction);
  }, [locomotive?.speed, locomotive?.direction]);

  function scheduleSpeed(nextSpeed: number) {
    setSpeed(nextSpeed);
    if (!throttleEnabled) return;
    if (throttleTimer.current !== null) window.clearTimeout(throttleTimer.current);
    throttleTimer.current = window.setTimeout(() => {
      run(() => api.setThrottle(address, nextSpeed, direction), false);
    }, 100);
  }

  async function changeDirection(nextDirection: "forward" | "reverse") {
    if (!validAddress || nextDirection === direction) return;
    if (speed > 0 && connected) {
      await run(() => api.stopLocomotive(address, direction), false);
      setSpeed(0);
    }
    setDirection(nextDirection);
  }

  async function toggleFunction(number: number, active: boolean) {
    if (pendingFunctions.has(number)) return;
    setPendingFunctions((current) => new Set(current).add(number));
    try {
      await run(() => api.setFunction(address, number, !active), false);
    } finally {
      setPendingFunctions((current) => {
        const next = new Set(current);
        next.delete(number);
        return next;
      });
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Union Pacific Layout</p>
          <h1>Railroad Control</h1>
        </div>
        <div className="header-actions">
          <span className={`connection connection--${state.connection.status}`}>
            {state.connection.status}
          </span>
          <button className="header-stop" disabled={!connected || busy} onClick={() => run(api.emergencyStop)}>E-STOP</button>
        </div>
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
          className="connection-action"
          disabled={busy || state.connection.status === "connecting"}
          onClick={() => run(connected ? api.disconnect : () => api.connect())}
        >
          {connected ? "Disconnect CSB1" : "Connect CSB1"}
        </button>
        <button
          className="power-action"
          disabled={!connected || busy}
          onClick={() => run(() => api.setPower(state.trackPower === "on" ? "off" : "on"))}
        >
          Power {state.trackPower === "on" ? "OFF" : "ON"}
        </button>
      </section>

      <section className="panel throttle-panel" aria-label="Locomotive throttle">
        <div className="throttle-heading">
          <div>
            <span className="label">Locomotive</span>
            <h2>Throttle</h2>
          </div>
        </div>

        <div className="roster-field">
          <span>Available locomotive</span>
          <button
            type="button"
            className="roster-trigger"
            aria-haspopup="listbox"
            aria-expanded={rosterOpen}
            onClick={() => setRosterOpen((open) => !open)}
          >
            <span>{selectedRoster ? `${selectedRoster.reportingMark} ${selectedRoster.roadNumber} — ${selectedRoster.prototype}` : "Select from active roster"}</span>
            <span aria-hidden="true">⌄</span>
          </button>
          {rosterOpen && (
            <div className="roster-options" role="listbox" aria-label="Active locomotives">
              {roster.map((item) => (
                <button
                  type="button"
                  role="option"
                  aria-selected={item.id === selectedRosterId}
                  key={item.id}
                  onClick={() => {
                    setSelectedRosterId(item.id);
                    setAddressText(String(item.address));
                    setSpeed(0);
                    setRosterOpen(false);
                  }}
                >
                  {item.reportingMark} {item.roadNumber} — {item.prototype}
                </button>
              ))}
              {roster.length === 0 && <p>No active locomotives</p>}
            </div>
          )}
        </div>
        {rosterError && <p className="roster-message" role="status">{rosterError}</p>}

        <label className="address-field">
          <span>Decoder-address override</span>
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            value={addressText}
            onChange={(event) => {
              setSelectedRosterId("");
              setAddressText(event.target.value.replace(/\D/g, ""));
              setSpeed(0);
            }}
            placeholder="DCC address"
            aria-invalid={addressText !== "" && !validAddress}
          />
        </label>

        <div className="direction-row" aria-label="Direction">
          <button className={direction === "reverse" ? "selected" : ""} disabled={!validAddress} onClick={() => changeDirection("reverse")}>Reverse</button>
          <button className={direction === "forward" ? "selected" : ""} disabled={!validAddress} onClick={() => changeDirection("forward")}>Forward</button>
        </div>

        <label className="speed-control">
          <span>Speed <strong>{speed}</strong></span>
          <input type="range" min="0" max="126" value={speed} disabled={!throttleEnabled} onChange={(event) => scheduleSpeed(Number(event.target.value))} />
        </label>

        <div className="function-toolbar">
          <button className="loco-stop" disabled={!connected || !validAddress} onClick={() => run(() => api.stopLocomotive(address, direction), false)}>
            Stop locomotive
          </button>
          <button
            type="button"
            className="function-bank"
            aria-label={`Show functions F${functionBank === 0 ? 16 : 0} through F${functionBank === 0 ? 31 : 15}`}
            onClick={() => setFunctionBank((bank) => bank === 0 ? 1 : 0)}
          >
            F{functionBank === 0 ? "16-F31" : "0-F15"}
          </button>
        </div>

        <div className="function-grid" aria-label={`Locomotive functions F${functionStart} through F${functionStart + 15}`}>
          {Array.from({ length: 16 }, (_, offset) => {
            const number = functionStart + offset;
            const active = Boolean(functions[String(number)]);
            return (
              <button
                key={number}
                className={active ? "active" : ""}
                aria-pressed={active}
                disabled={!throttleEnabled || pendingFunctions.has(number)}
                onClick={() => toggleFunction(number, active)}
              >
                <span>F{number}</span>
                <small>{number === 0 ? "Headlight" : number === 1 ? "Bell" : number === 2 ? "Horn" : "Sound"}</small>
              </button>
            );
          })}
        </div>
      </section>

    </main>
  );
}
