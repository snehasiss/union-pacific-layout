import type { RailroadState, RosterLocomotive } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers }
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error ?? `Request failed (${response.status})`);
  return body as T;
}

export const api = {
  status: () => request<RailroadState>("/api/v1/status"),
  locomotives: () => request<{ locomotives: RosterLocomotive[]; count: number }>("/api/v1/locomotives"),
  connect: (port?: string) =>
    request<{ connected: boolean; port: string }>("/api/v1/serial/connect", {
      method: "POST",
      body: JSON.stringify(port ? { port } : {})
    }),
  disconnect: () =>
    request<{ connected: boolean }>("/api/v1/serial/disconnect", { method: "POST" }),
  setPower: (state: "on" | "off") =>
    request("/api/v1/power", { method: "PUT", body: JSON.stringify({ state }) }),
  readCv: (cv: number) =>
    request<{ cv: number; value: number; confirmed: boolean; mode: "service" }>("/api/v1/programming/cv/read", {
      method: "POST",
      body: JSON.stringify({ cv })
    }),
  writeCv: (cv: number, value: number) =>
    request<{ cv: number; value: number; confirmed: boolean; mode: "service" }>("/api/v1/programming/cv", {
      method: "PUT",
      body: JSON.stringify({ cv, value })
    }),
  emergencyStop: () => request("/api/v1/emergency-stop", { method: "POST" }),
  setThrottle: (address: number, speed: number, direction: "forward" | "reverse") =>
    request(`/api/v1/locomotives/${address}/throttle`, {
      method: "PUT",
      body: JSON.stringify({ speed, direction })
    }),
  stopLocomotive: (address: number, direction: "forward" | "reverse") =>
    request(`/api/v1/locomotives/${address}/stop`, {
      method: "POST",
      body: JSON.stringify({ direction })
    }),
  setFunction: (address: number, number: number, active: boolean) =>
    request(`/api/v1/locomotives/${address}/functions/${number}`, {
      method: "PUT",
      body: JSON.stringify({ active })
    })
};
